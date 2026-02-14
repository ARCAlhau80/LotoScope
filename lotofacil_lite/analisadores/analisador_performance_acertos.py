#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🎯 ANALISADOR DE PERFORMANCE DE ACERTOS - LOTOFÁCIL
=====================================================

OTIMIZA A PERFORMANCE REAL DOS GERADORES:
✅ Análise de acertos históricos das combinações geradas
✅ Identificação de padrões que geram mais 12 e 13 pontos
✅ Otimização baseada em resultados reais
✅ Calibração dos algoritmos para máxima eficácia
✅ Relatórios detalhados de performance preditiva

FOCO: Aumentar significativamente os acertos de 12-13 pontos
"""

import os
import sys
import json
import time
from datetime import datetime, timedelta
from typing import List, Dict, Tuple, Optional
from collections import defaultdict
import statistics

# Adiciona o diretório pai ao sys.path
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
if parent_dir not in sys.path:
    sys.path.append(parent_dir)

# 🚀 SISTEMA DE OTIMIZAÇÃO DE BANCO
try:
    from database_optimizer import DatabaseOptimizer
    _db_optimizer = DatabaseOptimizer()
except ImportError:
    _db_optimizer = None

try:
    from database_config import DatabaseConfig
    from MenuLotofacil import MenuLotofacil
    from gerador_academico_dinamico import GeradorAcademicoDinamico
    from gerador_complementacao_inteligente import GeradorComplementacaoInteligente
except ImportError as e:
    print(f"⚠️ Erro de importação: {e}")

class AnalisadorPerformanceAcertos:
    """
    Analisador focado em melhorar a taxa de acertos das combinações
    Identifica padrões que levam a 12-13 pontos
    """
    
    def __init__(self):
        self.menu = None
        self.dados_historicos = []
        self.padroes_12_13_pontos = {}
        self.analise_cache = {}
        
        print("🎯 ANALISADOR DE PERFORMANCE DE ACERTOS")
        print("🏆 Foco: Maximizar combinações com 12-13 pontos")
        print("-" * 50)
        
        self._inicializar_sistema()
    
    def _inicializar_sistema(self):
        """Inicialização do sistema de análise"""
        try:
            self.menu = MenuLotofacil()
            if self.menu.testar_conexao():
                print("✅ Conexão com base de dados estabelecida")
            else:
                print("⚠️ Modo offline - análise limitada")
        except Exception as e:
            print(f"⚠️ Erro na inicialização: {e}")
    
    def carregar_dados_concursos_recentes(self, limite: int = 50) -> bool:
        """
        Carrega dados dos concursos mais recentes para análise
        """
        print(f"📊 Carregando últimos {limite} concursos...")
        
        try:
            if not self.menu or not self.menu.testar_conexao():
                print("❌ Sem conexão - usando dados simulados")
                return False
            
            # Query para pegar os últimos concursos
            query = f"""
            SELECT TOP {limite}
                Concurso,
                N1, N2, N3, N4, N5, N6, N7, N8, N9, N10, N11, N12, N13, N14, N15,
                DataSorteio
            FROM resultados_int 
            WHERE Concurso > (SELECT MAX(Concurso) - {limite} FROM resultados_int)
            ORDER BY Concurso DESC
            """
            
            resultados = self.menu.db_manager.executar_query(query)
            
            self.dados_historicos = []
            for resultado in resultados:
                concurso = resultado[0]
                numeros = [n for n in resultado[1:16] if n]  # N1 a N15
                data_sorteio = resultado[16] if len(resultado) > 16 else None
                
                self.dados_historicos.append({
                    'concurso': concurso,
                    'numeros': sorted(numeros),
                    'data': data_sorteio
                })
            
            print(f"✅ {len(self.dados_historicos)} concursos carregados")
            return True
            
        except Exception as e:
            print(f"❌ Erro no carregamento: {e}")
            return False
    
    def analisar_padroes_alto_desempenho(self) -> Dict:
        """
        Analisa padrões presentes nos concursos que podem levar a mais acertos
        """
        print("🔍 ANALISANDO PADRÕES DE ALTO DESEMPENHO...")
        print("-" * 50)
        
        if not self.dados_historicos:
            if not self.carregar_dados_concursos_recentes():
                return {}
        
        padroes = {
            'frequencias_otimas': {},
            'sequencias_eficazes': [],
            'distribuicoes_vencedoras': {},
            'padroes_pirâmide': {},
            'caracteristicas_premium': {}
        }
        
        # Análise de frequências dos números mais eficazes
        print("📊 Analisando frequências dos números...")
        contadores = defaultdict(int)
        
        for concurso in self.dados_historicos:
            for numero in concurso['numeros']:
                contadores[numero] += 1
        
        total_concursos = len(self.dados_historicos)
        for numero in range(1, 26):
            freq = contadores[numero] / total_concursos if total_concursos > 0 else 0
            padroes['frequencias_otimas'][numero] = freq
        
        # Análise de sequências mais eficazes
        print("🔄 Analisando sequências consecutivas...")
        for concurso in self.dados_historicos:
            numeros = concurso['numeros']
            seq_atual = 1
            max_seq = 1
            
            for i in range(1, len(numeros)):
                if numeros[i] == numeros[i-1] + 1:
                    seq_atual += 1
                    max_seq = max(max_seq, seq_atual)
                else:
                    seq_atual = 1
            
            if max_seq not in padroes['distribuicoes_vencedoras']:
                padroes['distribuicoes_vencedoras'][max_seq] = 0
            padroes['distribuicoes_vencedoras'][max_seq] += 1
        
        # Análise de distribuição por faixas
        print("📈 Analisando distribuições por faixas...")
        distribuicoes = {'baixa': [], 'media': [], 'alta': []}
        
        for concurso in self.dados_historicos:
            numeros = concurso['numeros']
            baixa = len([n for n in numeros if 1 <= n <= 8])
            media = len([n for n in numeros if 9 <= n <= 17])
            alta = len([n for n in numeros if 18 <= n <= 25])
            
            distribuicoes['baixa'].append(baixa)
            distribuicoes['media'].append(media)
            distribuicoes['alta'].append(alta)
        
        # Calcula médias e padrões ideais
        padroes['caracteristicas_premium'] = {
            'faixa_baixa_ideal': statistics.mean(distribuicoes['baixa']),
            'faixa_media_ideal': statistics.mean(distribuicoes['media']),
            'faixa_alta_ideal': statistics.mean(distribuicoes['alta']),
            'sequencia_media': statistics.mean([k for k, v in padroes['distribuicoes_vencedoras'].items() for _ in range(v)])
        }
        
        print("✅ Análise de padrões concluída!")
        return padroes
    
    def testar_combinacao_contra_historico(self, combinacao: List[int]) -> Dict:
        """
        Testa uma combinação específica contra o histórico
        Retorna estatísticas de performance
        """
        if not self.dados_historicos:
            return {'erro': 'Dados históricos não disponíveis'}
        
        acertos = []
        
        for concurso in self.dados_historicos:
            numeros_sorteados = set(concurso['numeros'])
            numeros_apostados = set(combinacao)
            acerto = len(numeros_sorteados.intersection(numeros_apostados))
            acertos.append(acerto)
        
        # Estatísticas detalhadas
        stats = {
            'total_testes': len(acertos),
            'acertos_11': acertos.count(11),
            'acertos_12': acertos.count(12),
            'acertos_13': acertos.count(13),
            'acertos_14': acertos.count(14),
            'acertos_15': acertos.count(15),
            'media_acertos': statistics.mean(acertos) if acertos else 0,
            'mediana_acertos': statistics.median(acertos) if acertos else 0,
            'acertos_12_13': acertos.count(12) + acertos.count(13),
            'performance_premium': (acertos.count(12) + acertos.count(13)) / len(acertos) * 100 if acertos else 0
        }
        
        return stats
    
    def avaliar_arquivo_combinacoes(self, caminho_arquivo: str) -> Dict:
        """
        Avalia todas as combinações de um arquivo gerado
        """
        print(f"📁 Avaliando arquivo: {os.path.basename(caminho_arquivo)}")
        
        if not os.path.exists(caminho_arquivo):
            return {'erro': f'Arquivo não encontrado: {caminho_arquivo}'}
        
        combinacoes = self._extrair_combinacoes_arquivo(caminho_arquivo)
        
        if not combinacoes:
            return {'erro': 'Nenhuma combinação encontrada no arquivo'}
        
        print(f"🎲 Testando {len(combinacoes)} combinações...")
        
        resultados = []
        for i, combinacao in enumerate(combinacoes):
            stats = self.testar_combinacao_contra_historico(combinacao)
            stats['combinacao_id'] = i + 1
            stats['combinacao'] = combinacao
            resultados.append(stats)
        
        # Análise consolidada
        analise_geral = self._analisar_resultados_consolidados(resultados)
        
        return {
            'arquivo': os.path.basename(caminho_arquivo),
            'total_combinacoes': len(combinacoes),
            'resultados_individuais': resultados,
            'analise_consolidada': analise_geral
        }
    
    def _extrair_combinacoes_arquivo(self, caminho: str) -> List[List[int]]:
        """Extrai combinações do arquivo (formato CHAVE DE OURO)"""
        combinacoes = []
        
        try:
            with open(caminho, 'r', encoding='utf-8') as f:
                conteudo = f.read()
            
            # Procura pela seção CHAVE DE OURO
            if 'CHAVE DE OURO' in conteudo:
                linhas = conteudo.split('\n')
                capturando = False
                
                for linha in linhas:
                    if 'CHAVE DE OURO' in linha:
                        capturando = True
                        continue
                    
                    if capturando and linha.strip():
                        # Formato: 01: 02,03,05,07,09...
                        if ':' in linha:
                            numeros_str = linha.split(':', 1)[1].strip()
                            try:
                                numeros = [int(n.strip()) for n in numeros_str.split(',')]
                                if all(1 <= n <= 25 for n in numeros):
                                    combinacoes.append(sorted(numeros))
                            except ValueError:
                                continue
                        elif linha.strip() and all(c in '0123456789,' for c in linha.replace(' ', '')):
                            # Linha só com números
                            try:
                                numeros = [int(n.strip()) for n in linha.split(',')]
                                if all(1 <= n <= 25 for n in numeros):
                                    combinacoes.append(sorted(numeros))
                            except ValueError:
                                continue
            
        except Exception as e:
            print(f"❌ Erro ao extrair combinações: {e}")
        
        return combinacoes
    
    def _analisar_resultados_consolidados(self, resultados: List[Dict]) -> Dict:
        """Análise consolidada dos resultados"""
        if not resultados:
            return {}
        
        # Coleta todas as métricas
        todas_medias = [r['media_acertos'] for r in resultados]
        todos_12 = [r['acertos_12'] for r in resultados]
        todos_13 = [r['acertos_13'] for r in resultados]
        performance_premium = [r['performance_premium'] for r in resultados]
        
        # Encontra as melhores combinações
        melhor_media = max(resultados, key=lambda x: x['media_acertos'])
        melhor_12_13 = max(resultados, key=lambda x: x['acertos_12_13'])
        melhor_premium = max(resultados, key=lambda x: x['performance_premium'])
        
        analise = {
            'performance_geral': {
                'media_acertos_geral': statistics.mean(todas_medias),
                'media_12_pontos': statistics.mean(todos_12),
                'media_13_pontos': statistics.mean(todos_13),
                'performance_premium_media': statistics.mean(performance_premium)
            },
            'melhores_combinacoes': {
                'melhor_media_acertos': {
                    'id': melhor_media['combinacao_id'],
                    'combinacao': melhor_media['combinacao'],
                    'media_acertos': melhor_media['media_acertos'],
                    'acertos_12_13': melhor_media['acertos_12_13']
                },
                'melhor_12_13_pontos': {
                    'id': melhor_12_13['combinacao_id'],
                    'combinacao': melhor_12_13['combinacao'],
                    'acertos_12_13': melhor_12_13['acertos_12_13'],
                    'performance_premium': melhor_12_13['performance_premium']
                },
                'melhor_performance_premium': {
                    'id': melhor_premium['combinacao_id'],
                    'combinacao': melhor_premium['combinacao'],
                    'performance_premium': melhor_premium['performance_premium']
                }
            },
            'distribuicao_acertos': {
                'combinacoes_com_12+': len([r for r in resultados if r['acertos_12'] > 0]),
                'combinacoes_com_13+': len([r for r in resultados if r['acertos_13'] > 0]),
                'total_12_pontos': sum(todos_12),
                'total_13_pontos': sum(todos_13)
            }
        }
        
        return analise
    
    def gerar_relatorio_performance(self, analise: Dict, salvar_arquivo: bool = True) -> str:
        """Gera relatório detalhado de performance"""
        relatorio_linhas = []
        
        relatorio_linhas.append("🏆 RELATÓRIO DE PERFORMANCE DE ACERTOS - LOTOFÁCIL")
        relatorio_linhas.append("=" * 70)
        relatorio_linhas.append(f"📊 Data/Hora: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
        relatorio_linhas.append(f"📁 Arquivo analisado: {analise.get('arquivo', 'N/A')}")
        relatorio_linhas.append(f"🎲 Total de combinações: {analise.get('total_combinacoes', 0)}")
        relatorio_linhas.append("")
        
        # Performance Geral
        if 'analise_consolidada' in analise:
            consolidada = analise['analise_consolidada']
            perf_geral = consolidada.get('performance_geral', {})
            
            relatorio_linhas.append("📈 PERFORMANCE GERAL:")
            relatorio_linhas.append("-" * 40)
            relatorio_linhas.append(f"• Média de acertos: {perf_geral.get('media_acertos_geral', 0):.2f}")
            relatorio_linhas.append(f"• Média de 12 pontos: {perf_geral.get('media_12_pontos', 0):.2f}")
            relatorio_linhas.append(f"• Média de 13 pontos: {perf_geral.get('media_13_pontos', 0):.2f}")
            relatorio_linhas.append(f"• Performance Premium (12+13): {perf_geral.get('performance_premium_media', 0):.2f}%")
            relatorio_linhas.append("")
            
            # Melhores Combinações
            melhores = consolidada.get('melhores_combinacoes', {})
            
            relatorio_linhas.append("🥇 MELHORES COMBINAÇÕES:")
            relatorio_linhas.append("-" * 40)
            
            if 'melhor_12_13_pontos' in melhores:
                melhor = melhores['melhor_12_13_pontos']
                nums = ','.join([f"{n:02d}" for n in melhor['combinacao']])
                relatorio_linhas.append(f"🎯 Mais 12+13 pontos: {nums}")
                relatorio_linhas.append(f"   • Total 12+13: {melhor['acertos_12_13']}")
                relatorio_linhas.append(f"   • Performance: {melhor['performance_premium']:.2f}%")
                relatorio_linhas.append("")
            
            if 'melhor_media_acertos' in melhores:
                melhor = melhores['melhor_media_acertos']
                nums = ','.join([f"{n:02d}" for n in melhor['combinacao']])
                relatorio_linhas.append(f"📊 Melhor média geral: {nums}")
                relatorio_linhas.append(f"   • Média de acertos: {melhor['media_acertos']:.2f}")
                relatorio_linhas.append("")
            
            # Distribuição
            distrib = consolidada.get('distribuicao_acertos', {})
            relatorio_linhas.append("📊 DISTRIBUIÇÃO DE ACERTOS:")
            relatorio_linhas.append("-" * 40)
            relatorio_linhas.append(f"• Combinações com 12+ pontos: {distrib.get('combinacoes_com_12+', 0)}")
            relatorio_linhas.append(f"• Combinações com 13+ pontos: {distrib.get('combinacoes_com_13+', 0)}")
            relatorio_linhas.append(f"• Total de 12 pontos: {distrib.get('total_12_pontos', 0)}")
            relatorio_linhas.append(f"• Total de 13 pontos: {distrib.get('total_13_pontos', 0)}")
            relatorio_linhas.append("")
        
        # Recomendações
        relatorio_linhas.append("💡 RECOMENDAÇÕES PARA MELHORIA:")
        relatorio_linhas.append("-" * 40)
        relatorio_linhas.append("• Use as combinações com melhor performance premium")
        relatorio_linhas.append("• Analise os padrões das combinações top performers")
        relatorio_linhas.append("• Considere ajustar algoritmos baseado nestes resultados")
        relatorio_linhas.append("• Foque em padrões que geram mais 12-13 pontos")
        
        relatorio_texto = "\n".join(relatorio_linhas)
        
        if salvar_arquivo:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            nome_arquivo = f"relatorio_performance_acertos_{timestamp}.txt"
            caminho = os.path.join(os.path.dirname(__file__), nome_arquivo)
            
            try:
                with open(caminho, 'w', encoding='utf-8') as f:
                    f.write(relatorio_texto)
                print(f"💾 Relatório salvo: {nome_arquivo}")
            except Exception as e:
                print(f"❌ Erro ao salvar relatório: {e}")
        
        return relatorio_texto
    
    def executar_menu_principal(self):
        """Menu principal do analisador"""
        while True:
            print("\n" + "=" * 70)
            print("🎯 ANALISADOR DE PERFORMANCE DE ACERTOS")
            print("=" * 70)
            print("🏆 Otimiza geradores para máximos 12-13 pontos")
            print("=" * 70)
            print("1️⃣  📊 Analisar Arquivo de Combinações")
            print("2️⃣  🔍 Testar Combinação Específica")
            print("3️⃣  📈 Analisar Padrões de Alto Desempenho")
            print("4️⃣  🎲 Avaliar Múltiplos Arquivos")
            print("5️⃣  ⚙️ Configurar Análise")
            print("0️⃣  🚪 Sair")
            print("=" * 70)
            
            try:
                opcao = input("Escolha uma opção (0-5): ").strip()
                
                if opcao == "1":
                    self._executar_analise_arquivo()
                elif opcao == "2":
                    self._executar_teste_combinacao()
                elif opcao == "3":
                    self._executar_analise_padroes()
                elif opcao == "4":
                    self._executar_analise_multiplos()
                elif opcao == "5":
                    self._executar_configuracao()
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
    
    def _executar_analise_arquivo(self):
        """Executa análise de arquivo específico"""
        print("\n📊 ANÁLISE DE ARQUIVO DE COMBINAÇÕES")
        print("-" * 50)
        
        # Lista arquivos disponíveis
        arquivos = [f for f in os.listdir('.') if f.startswith('combinacoes_') and f.endswith('.txt')]
        
        if not arquivos:
            print("❌ Nenhum arquivo de combinações encontrado")
            return
        
        print("📁 Arquivos disponíveis:")
        for i, arquivo in enumerate(arquivos, 1):
            print(f"   {i}. {arquivo}")
        
        try:
            escolha = int(input(f"\nEscolha um arquivo (1-{len(arquivos)}): ")) - 1
            if 0 <= escolha < len(arquivos):
                arquivo_escolhido = arquivos[escolha]
                
                print(f"\n🔍 Analisando {arquivo_escolhido}...")
                analise = self.avaliar_arquivo_combinacoes(arquivo_escolhido)
                
                if 'erro' in analise:
                    print(f"❌ Erro: {analise['erro']}")
                else:
                    relatorio = self.gerar_relatorio_performance(analise)
                    print("\n" + relatorio)
            else:
                print("❌ Escolha inválida!")
                
        except ValueError:
            print("❌ Por favor, digite um número válido")
        except Exception as e:
            print(f"❌ Erro na análise: {e}")
    
    def _executar_teste_combinacao(self):
        """Testa combinação específica"""
        print("\n🔍 TESTE DE COMBINAÇÃO ESPECÍFICA")
        print("-" * 40)
        
        try:
            entrada = input("Digite os números (ex: 1,2,3,4,5,6,7,8,9,10,11,12,13,14,15): ")
            numeros = [int(n.strip()) for n in entrada.split(',')]
            
            if len(numeros) < 15 or len(numeros) > 20:
                print("❌ Digite entre 15 e 20 números")
                return
            
            if not all(1 <= n <= 25 for n in numeros):
                print("❌ Números devem estar entre 1 e 25")
                return
            
            print(f"\n🎲 Testando combinação: {sorted(numeros)}")
            stats = self.testar_combinacao_contra_historico(numeros)
            
            print("\n📊 RESULTADOS:")
            print(f"• Total de testes: {stats['total_testes']}")
            print(f"• Média de acertos: {stats['media_acertos']:.2f}")
            print(f"• Acertos de 12: {stats['acertos_12']}")
            print(f"• Acertos de 13: {stats['acertos_13']}")
            print(f"• Performance Premium: {stats['performance_premium']:.2f}%")
            
        except ValueError:
            print("❌ Formato inválido. Use vírgulas entre os números")
        except Exception as e:
            print(f"❌ Erro no teste: {e}")
    
    def _executar_analise_padroes(self):
        """Executa análise de padrões"""
        print("\n📈 ANÁLISE DE PADRÕES DE ALTO DESEMPENHO")
        print("-" * 50)
        
        padroes = self.analisar_padroes_alto_desempenho()
        
        if padroes:
            print("\n🏆 FREQUÊNCIAS ÓTIMAS (Top 10):")
            freqs = padroes['frequencias_otimas']
            top_freq = sorted(freqs.items(), key=lambda x: x[1], reverse=True)[:10]
            
            for i, (numero, freq) in enumerate(top_freq, 1):
                print(f"   {i:2d}. Número {numero:2d}: {freq:.3f}")
            
            print(f"\n📊 CARACTERÍSTICAS IDEAIS:")
            caract = padroes['caracteristicas_premium']
            print(f"• Faixa Baixa (1-8): {caract['faixa_baixa_ideal']:.1f} números")
            print(f"• Faixa Média (9-17): {caract['faixa_media_ideal']:.1f} números")
            print(f"• Faixa Alta (18-25): {caract['faixa_alta_ideal']:.1f} números")
            print(f"• Sequência Média: {caract['sequencia_media']:.1f}")
    
    def _executar_analise_multiplos(self):
        """Análise de múltiplos arquivos"""
        print("\n🎲 ANÁLISE DE MÚLTIPLOS ARQUIVOS")
        print("-" * 40)
        
        arquivos = [f for f in os.listdir('.') if f.startswith('combinacoes_') and f.endswith('.txt')]
        
        if len(arquivos) < 2:
            print("❌ Precisa de pelo menos 2 arquivos para comparação")
            return
        
        print("🔍 Analisando todos os arquivos encontrados...")
        
        resultados_gerais = []
        
        for arquivo in arquivos:
            print(f"   Processando: {arquivo}")
            analise = self.avaliar_arquivo_combinacoes(arquivo)
            
            if 'erro' not in analise:
                consolidada = analise.get('analise_consolidada', {})
                perf_geral = consolidada.get('performance_geral', {})
                
                resultados_gerais.append({
                    'arquivo': arquivo,
                    'media_acertos': perf_geral.get('media_acertos_geral', 0),
                    'performance_premium': perf_geral.get('performance_premium_media', 0),
                    'total_combinacoes': analise.get('total_combinacoes', 0)
                })
        
        if resultados_gerais:
            print("\n🏆 RANKING DE ARQUIVOS:")
            resultados_gerais.sort(key=lambda x: x['performance_premium'], reverse=True)
            
            for i, resultado in enumerate(resultados_gerais, 1):
                print(f"{i:2d}. {resultado['arquivo'][:40]}")
                print(f"     Performance Premium: {resultado['performance_premium']:.2f}%")
                print(f"     Média de acertos: {resultado['media_acertos']:.2f}")
                print()
    
    def _executar_configuracao(self):
        """Configurações do analisador"""
        print("\n⚙️ CONFIGURAÇÕES")
        print("-" * 30)
        
        print("1. Recarregar dados históricos")
        print("2. Configurar quantidade de concursos para análise")
        print("3. Voltar")
        
        opcao = input("Escolha (1-3): ").strip()
        
        if opcao == "1":
            print("🔄 Recarregando dados...")
            self.dados_historicos = []
            self.carregar_dados_concursos_recentes()
        elif opcao == "2":
            try:
                limite = int(input("Quantidade de concursos (10-200): "))
                if 10 <= limite <= 200:
                    print(f"🔄 Carregando {limite} concursos...")
                    self.carregar_dados_concursos_recentes(limite)
                else:
                    print("❌ Valor deve estar entre 10 e 200")
            except ValueError:
                print("❌ Digite um número válido")

def main():
    """Função principal"""
    analisador = AnalisadorPerformanceAcertos()
    analisador.executar_menu_principal()

if __name__ == "__main__":
    main()
