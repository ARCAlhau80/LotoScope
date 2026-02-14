#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🎯 GERADOR BASEADO NO NÚCLEO COMPORTAMENTAL
==========================================
Gerador inteligente que usa análise comportamental dos números
para criar combinações otimizadas da Lotofácil.

Sistema baseado em:
- Análise de padrões comportamentais em janelas de 15 concursos
- Núcleo dos 10 melhores números por score comportamental
- Estratégias adaptativas de complementação
- Parâmetro dinâmico de último concurso para testes

Uso:
    python gerador_nucleo_comportamental.py [ultimo_concurso] [qtd_jogos]
"""

import sys
import os
from pathlib import Path
_BASE_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(_BASE_DIR))
sys.path.insert(0, str(_BASE_DIR / 'utils'))
sys.path.insert(0, str(_BASE_DIR / 'analisadores'))

from analisador_comportamento_numerico import AnalisadorComportamentoNumerico
from database_config import DatabaseConfig

# 🚀 SISTEMA DE OTIMIZAÇÃO DE BANCO
try:
    from database_optimizer import DatabaseOptimizer
    _db_optimizer = DatabaseOptimizer()
except ImportError:
    _db_optimizer = None

from datetime import datetime
import random
import itertools

class GeradorNucleoComportamental:
    """Gerador baseado em análise comportamental dos números"""
    
    def __init__(self, ultimo_concurso=None):
        """
        Inicializa o gerador
        
        Args:
            ultimo_concurso (int, optional): Último concurso para análise
        """
        self.ultimo_concurso = ultimo_concurso
        self.nucleo_comportamental = []
        self.analises_completas = {}
        self.complementares = []
        
        print("🎯 GERADOR NÚCLEO COMPORTAMENTAL INICIALIZADO")
        
    def executar_analise_comportamental(self):
        """Executa a análise comportamental para obter o núcleo"""
        print("\n🧠 Executando análise comportamental...")
        
        analisador = AnalisadorComportamentoNumerico(self.ultimo_concurso)
        analises = analisador.analisar_todos_numeros()
        nucleo, _ = analisador.obter_top_10_numeros(analises)
        
        self.nucleo_comportamental = nucleo
        self.analises_completas = analises
        
        # Define complementares (os 15 números restantes)
        self.complementares = [n for n in range(1, 26) if n not in nucleo]
        
        print(f"✅ Núcleo comportamental definido: {sorted(nucleo)}")
        print(f"📦 Números complementares: {sorted(self.complementares)}")
        
        return nucleo
    
    def analisar_complementares(self):
        """Analisa e ordena os números complementares por score"""
        complementares_com_score = []
        
        for numero in self.complementares:
            if numero in self.analises_completas:
                analise = self.analises_completas[numero]
                complementares_com_score.append({
                    'numero': numero,
                    'score': analise['score'],
                    'comportamento': analise['comportamento'],
                    'frequencia': analise['frequencia'],
                    'estado': analise['estado_atual']['estado']
                })
        
        # Ordena por score decrescente
        complementares_com_score.sort(key=lambda x: x['score'], reverse=True)
        
        print(f"\n📊 ANÁLISE DOS COMPLEMENTARES:")
        for i, comp in enumerate(complementares_com_score[:10], 1):
            estado_emoji = "🔥" if comp['estado'] == 'em_sequencia' else "❄️"
            print(f"   {i:2d}º: Número {comp['numero']:2d} - Score {comp['score']:5.1f} {estado_emoji}")
        
        return complementares_com_score
    
    def estrategia_nucleo_fixo(self, qtd_jogos=5):
        """
        Estratégia 1: Núcleo fixo (10 números sempre) + 5 complementares rotativos
        
        Args:
            qtd_jogos (int): Quantidade de jogos a gerar
            
        Returns:
            list: Lista de combinações geradas
        """
        print(f"\n🎯 ESTRATÉGIA: NÚCLEO FIXO + COMPLEMENTARES ROTATIVOS")
        print(f"💡 Conceito: 10 melhores sempre + 5 complementares variados")
        
        complementares_ordenados = self.analisar_complementares()
        jogos = []
        
        for i in range(qtd_jogos):
            # Sempre incluir o núcleo completo
            jogo = self.nucleo_comportamental.copy()
            
            # Selecionar 5 complementares de forma inteligente
            # Mistura os melhores com alguns aleatórios
            top_complementares = [c['numero'] for c in complementares_ordenados[:8]]  # Top 8
            outros_complementares = [c['numero'] for c in complementares_ordenados[8:]]  # Outros
            
            # 3 dos top + 2 dos outros
            selecionados = random.sample(top_complementares, 3) + random.sample(outros_complementares, 2)
            
            jogo.extend(selecionados)
            jogo.sort()
            jogos.append(jogo)
            
            print(f"Jogo {i+1:2d}: {jogo}")
            print(f"         Complementares: {sorted(selecionados)}")
        
        return jogos
    
    def estrategia_escalonada(self, qtd_jogos=5):
        """
        Estratégia 2: Escalonamento por performance comportamental
        
        Args:
            qtd_jogos (int): Quantidade de jogos a gerar
            
        Returns:
            list: Lista de combinações geradas
        """
        print(f"\n📊 ESTRATÉGIA: ESCALONAMENTO POR COMPORTAMENTO")
        print(f"💡 Conceito: Peso maior nos 5 primeiros, rotação dos demais")
        
        # Divide o núcleo em prioritários e rotativos
        prioritarios = self.nucleo_comportamental[:5]  # Top 5 sempre
        rotativos_nucleo = self.nucleo_comportamental[5:]  # 5 rotativos do núcleo
        
        complementares_ordenados = self.analisar_complementares()
        top_complementares = [c['numero'] for c in complementares_ordenados[:10]]
        
        jogos = []
        
        print(f"🏆 Núcleo prioritário (sempre): {prioritarios}")
        print(f"🔄 Núcleo rotativo: {rotativos_nucleo}")
        
        for i in range(qtd_jogos):
            jogo = prioritarios.copy()  # Sempre os 5 prioritários
            
            # 3-4 do núcleo rotativo
            qtd_rotativos = random.choice([3, 4])
            selecionados_rotativos = random.sample(rotativos_nucleo, qtd_rotativos)
            jogo.extend(selecionados_rotativos)
            
            # Completar com complementares (15 - 5 - qtd_rotativos)
            qtd_complementares = 15 - 5 - qtd_rotativos
            selecionados_complementares = random.sample(top_complementares, qtd_complementares)
            jogo.extend(selecionados_complementares)
            
            jogo.sort()
            jogos.append(jogo)
            
            print(f"Jogo {i+1:2d}: {jogo}")
            print(f"         Rotativos: {sorted(selecionados_rotativos)} | Complementares: {sorted(selecionados_complementares)}")
        
        return jogos
    
    def estrategia_comportamental_pura(self, qtd_jogos=5):
        """
        Estratégia 3: Seleção puramente baseada em comportamento
        
        Args:
            qtd_jogos (int): Quantidade de jogos a gerar
            
        Returns:
            list: Lista de combinações geradas
        """
        print(f"\n🧠 ESTRATÉGIA: COMPORTAMENTAL PURA")
        print(f"💡 Conceito: Seleção baseada apenas no comportamento atual")
        
        # Classifica todos os 25 números por score
        todos_numeros = []
        for numero in range(1, 26):
            if numero in self.analises_completas:
                analise = self.analises_completas[numero]
                todos_numeros.append({
                    'numero': numero,
                    'score': analise['score'],
                    'comportamento': analise['comportamento'],
                    'estado': analise['estado_atual']
                })
        
        todos_numeros.sort(key=lambda x: x['score'], reverse=True)
        
        jogos = []
        
        for i in range(qtd_jogos):
            # Estratégia adaptativa baseada no comportamento
            jogo = []
            
            # Sempre pegar os 8 primeiros (mais estáveis)
            jogo.extend([n['numero'] for n in todos_numeros[:8]])
            
            # Para os 7 restantes, usar lógica comportamental
            candidatos = todos_numeros[8:]
            
            # Priorizar números em sequência (tendência de continuar)
            em_sequencia = [n for n in candidatos if n['estado']['estado'] == 'em_sequencia']
            em_pausa_longa = [n for n in candidatos if n['estado']['estado'] == 'em_pausa' and n['estado']['tamanho'] >= 3]
            
            # 3-4 em sequência + 3-4 em pausa longa
            qtd_sequencia = min(4, len(em_sequencia))
            qtd_pausa = 7 - qtd_sequencia
            
            if qtd_sequencia > 0:
                selecionados_seq = random.sample(em_sequencia, qtd_sequencia)
                jogo.extend([n['numero'] for n in selecionados_seq])
            
            if qtd_pausa > 0 and em_pausa_longa:
                qtd_pausa = min(qtd_pausa, len(em_pausa_longa))
                selecionados_pausa = random.sample(em_pausa_longa, qtd_pausa)
                jogo.extend([n['numero'] for n in selecionados_pausa])
            
            # Completa com os melhores se necessário
            while len(jogo) < 15:
                for n in candidatos:
                    if n['numero'] not in jogo:
                        jogo.append(n['numero'])
                        break
            
            jogo.sort()
            jogos.append(jogo)
            
            print(f"Jogo {i+1:2d}: {jogo}")
        
        return jogos
    
    def estrategia_hibrida(self, qtd_jogos=8):
        """
        Estratégia 4: Híbrida - combina todas as estratégias anteriores
        
        Args:
            qtd_jogos (int): Quantidade de jogos a gerar
            
        Returns:
            list: Lista de combinações geradas
        """
        print(f"\n⭐ ESTRATÉGIA: HÍBRIDA - MÚLTIPLAS ABORDAGENS")
        print(f"💡 Conceito: Combina todas as estratégias comportamentais")
        
        jogos = []
        
        # Distribui jogos entre as estratégias
        qtd_por_estrategia = max(1, qtd_jogos // 3)
        
        # Estratégia 1: Núcleo fixo
        jogos_nucleo = self.estrategia_nucleo_fixo(qtd_por_estrategia)
        for i, jogo in enumerate(jogos_nucleo):
            jogos.append(jogo)
            print(f"Híbrido {len(jogos):2d}: {jogo} (Núcleo Fixo)")
        
        # Estratégia 2: Escalonada
        jogos_escalonada = self.estrategia_escalonada(qtd_por_estrategia)
        for i, jogo in enumerate(jogos_escalonada):
            jogos.append(jogo)
            print(f"Híbrido {len(jogos):2d}: {jogo} (Escalonada)")
        
        # Estratégia 3: Comportamental pura
        restante = qtd_jogos - len(jogos)
        if restante > 0:
            jogos_comportamental = self.estrategia_comportamental_pura(restante)
            for i, jogo in enumerate(jogos_comportamental):
                jogos.append(jogo)
                print(f"Híbrido {len(jogos):2d}: {jogo} (Comportamental)")
        
        return jogos
    
    def salvar_combinacoes(self, jogos, estrategia_nome):
        """Salva as combinações em arquivo"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        periodo = f"{self.ultimo_concurso-14}_{self.ultimo_concurso}" if self.ultimo_concurso else "atual"
        arquivo = f"combinacoes_comportamental_{estrategia_nome.lower()}_{periodo}_{timestamp}.txt"
        
        with open(arquivo, 'w', encoding='utf-8') as f:
            f.write(f"🎯 COMBINAÇÕES BASEADAS EM ANÁLISE COMPORTAMENTAL\n")
            f.write(f"Estratégia: {estrategia_nome}\n")
            f.write(f"Período de análise: {self.ultimo_concurso-14 if self.ultimo_concurso else 'Atual'} a {self.ultimo_concurso or 'Atual'}\n")
            f.write(f"Núcleo comportamental: {sorted(self.nucleo_comportamental)}\n")
            f.write(f"Data/Hora: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}\n")
            f.write(f"Total de jogos: {len(jogos)}\n\n")
            
            for i, jogo in enumerate(jogos, 1):
                f.write(f"Jogo {i:2d}: {jogo}\n")
            
            f.write(f"\n{'='*50}\n")
            f.write(f"🔑 CHAVE DE OURO - FORMATO COMPACTO\n")
            f.write(f"{'='*50}\n")
            
            for i, jogo in enumerate(jogos, 1):
                nums_str = ','.join([f"{n:02d}" for n in jogo])
                f.write(f"{nums_str}\n")
        
        print(f"\n💾 Combinações salvas: {arquivo}")
        return arquivo
    
    def menu_interativo(self):
        """Menu interativo para seleção de estratégias"""
        print(f"\n{'='*60}")
        print(f"🎯 GERADOR NÚCLEO COMPORTAMENTAL")
        print(f"{'='*60}")
        print(f"🧠 Baseado em análise de padrões comportamentais")
        
        if self.ultimo_concurso:
            print(f"📅 Período: {self.ultimo_concurso-14} a {self.ultimo_concurso}")
        else:
            print(f"📅 Período: Últimos 15 concursos da base")
        
        print(f"🔥 Núcleo: {sorted(self.nucleo_comportamental)}")
        print(f"{'='*60}")
        
        print(f"1️⃣  🎯 Estratégia Núcleo Fixo (10 sempre + 5 variáveis)")
        print(f"2️⃣  📊 Estratégia Escalonada (5 prioritários + rotação)")
        print(f"3️⃣  🧠 Estratégia Comportamental Pura")
        print(f"4️⃣  ⭐ Estratégia Híbrida (todas combinadas)")
        print(f"5️⃣  📋 Relatório Comportamental Completo")
        print(f"0️⃣  🚪 Sair")
        print(f"{'='*60}")
        
        while True:
            try:
                opcao = input("Escolha uma opção (0-5): ").strip()
                
                if opcao == '0':
                    print("👋 Até logo!")
                    return
                
                elif opcao == '1':
                    qtd = int(input("Quantas combinações (padrão 5): ") or "5")
                    jogos = self.estrategia_nucleo_fixo(qtd)
                    self.salvar_combinacoes(jogos, "Nucleo_Fixo")
                    
                elif opcao == '2':
                    qtd = int(input("Quantas combinações (padrão 5): ") or "5")
                    jogos = self.estrategia_escalonada(qtd)
                    self.salvar_combinacoes(jogos, "Escalonada")
                    
                elif opcao == '3':
                    qtd = int(input("Quantas combinações (padrão 5): ") or "5")
                    jogos = self.estrategia_comportamental_pura(qtd)
                    self.salvar_combinacoes(jogos, "Comportamental_Pura")
                    
                elif opcao == '4':
                    qtd = int(input("Quantas combinações (padrão 8): ") or "8")
                    jogos = self.estrategia_hibrida(qtd)
                    self.salvar_combinacoes(jogos, "Hibrida")
                    
                elif opcao == '5':
                    self.gerar_relatorio_comportamental()
                    
                else:
                    print("⚠️ Opção inválida!")
                
                input("\nPressione ENTER para continuar...")
                print(f"\n{'='*60}")
                
            except KeyboardInterrupt:
                print("\n👋 Até logo!")
                break
            except Exception as e:
                print(f"❌ Erro: {e}")
    
    def gerar_relatorio_comportamental(self):
        """Gera relatório detalhado do comportamento dos números"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        arquivo = f"relatorio_comportamental_{timestamp}.txt"
        
        with open(arquivo, 'w', encoding='utf-8') as f:
            f.write(f"📋 RELATÓRIO COMPORTAMENTAL COMPLETO\n")
            f.write(f"{'='*60}\n")
            f.write(f"📅 Período: {self.ultimo_concurso-14 if self.ultimo_concurso else 'Atual'} a {self.ultimo_concurso or 'Atual'}\n")
            f.write(f"🕐 Data: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}\n\n")
            
            f.write(f"🏆 NÚCLEO COMPORTAMENTAL (TOP 10):\n")
            f.write(f"{sorted(self.nucleo_comportamental)}\n\n")
            
            f.write(f"📊 ANÁLISE DETALHADA POR NÚMERO:\n")
            f.write(f"{'='*60}\n")
            
            # Ordena todos os números por score
            numeros_ordenados = sorted(self.analises_completas.items(), 
                                     key=lambda x: x[1]['score'], reverse=True)
            
            for numero, analise in numeros_ordenados:
                f.write(f"\nNúmero {numero:2d} - Score: {analise['score']:5.1f}\n")
                f.write(f"Frequência: {analise['frequencia']:.1%} ({sum(analise['aparicoes'])}/15)\n")
                f.write(f"Comportamento: {analise['comportamento'].replace('_', ' ')}\n")
                f.write(f"Estado atual: {analise['estado_atual']['estado'].replace('_', ' ')}\n")
                f.write(f"Duração atual: {analise['estado_atual']['tamanho']} concursos\n")
                f.write(f"Tendência: {analise['estado_atual']['tendencia']:.1%}\n")
                
                if analise['sequencias']:
                    f.write(f"Sequências: {analise['sequencias']} (média: {analise['metricas']['sequencia_media']:.1f})\n")
                if analise['pausas']:
                    f.write(f"Pausas: {analise['pausas']} (média: {analise['metricas']['pausa_media']:.1f})\n")
        
        print(f"\n📋 Relatório comportamental salvo: {arquivo}")

def main():
    """Função principal"""
    # Parâmetros da linha de comando
    ultimo_concurso = None
    qtd_jogos = 5
    
    if len(sys.argv) > 1:
        try:
            ultimo_concurso = int(sys.argv[1])
        except ValueError:
            print("⚠️ Parâmetro último_concurso inválido")
    
    if len(sys.argv) > 2:
        try:
            qtd_jogos = int(sys.argv[2])
        except ValueError:
            print("⚠️ Parâmetro qtd_jogos inválido")
    
    try:
        # Inicializa gerador
        gerador = GeradorNucleoComportamental(ultimo_concurso)
        
        # Executa análise comportamental
        gerador.executar_analise_comportamental()
        
        # Menu interativo
        gerador.menu_interativo()
        
    except Exception as e:
        print(f"❌ ERRO: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())
