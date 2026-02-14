#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🚀 SISTEMA INTEGRADO DE ANÁLISE AVANÇADA
Combina todos os sistemas avançados desenvolvidos
Autor: AR CALHAU
Data: 13 de Agosto de 2025
"""

import subprocess
import sys
import os
from datetime import datetime
from pathlib import Path

# Configurar paths para imports
_BASE_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(_BASE_DIR))
sys.path.insert(0, str(_BASE_DIR / 'utils'))

from database_config import db_config

# 🚀 SISTEMA DE OTIMIZAÇÃO DE BANCO
try:
    from database_optimizer import DatabaseOptimizer
    _db_optimizer = DatabaseOptimizer()
except ImportError:
    _db_optimizer = None


class SistemaIntegradoAvancado:
    """Sistema que integra todas as funcionalidades avançadas"""
    
    def __init__(self):
        self.sistemas_disponiveis = {
            'inteligencia': {
                'nome': '🧠 Inteligência Preditiva',
                'arquivo': 'sistema_inteligencia_preditiva.py',
                'descricao': 'Análise multi-dimensional com ciclos numéricos e previsões neurais'
            },
            'adaptativa': {
                'nome': '🔮 Previsão Adaptativa',
                'arquivo': 'sistema_previsao_adaptativa.py',
                'descricao': 'Machine learning temporal com padrões sazonais'
            },
            'probabilistica': {
                'nome': '🎯 Otimização Probabilística',
                'arquivo': 'sistema_otimizacao_probabilistica.py',
                'descricao': 'Análise probabilística com matriz de co-ocorrência'
            }
        }

    def mostrar_menu_avancado(self):
        """Mostra menu dos sistemas avançados"""
        print("\n🚀 SISTEMAS DE ANÁLISE AVANÇADA")
        print("=" * 45)
        print("1 - 🧠 Inteligência Preditiva (ciclos + neural)")
        print("2 - 🔮 Previsão Adaptativa (machine learning)")
        print("3 - 🎯 Otimização Probabilística (co-ocorrência)")
        print("4 - 🎪 EXECUTAR TODOS OS SISTEMAS (análise completa)")
        print("5 - 📊 Comparar resultados dos sistemas")
        print("6 - 🎯 Gerar super-combinação híbrida")
        print("0 - Voltar ao menu principal")

    def executar_sistema(self, tipo_sistema: str) -> bool:
        """Executa um sistema específico"""
        if tipo_sistema not in self.sistemas_disponiveis:
            print(f"❌ Sistema '{tipo_sistema}' não encontrado")
            return False
        
        sistema = self.sistemas_disponiveis[tipo_sistema]
        arquivo = sistema['arquivo']
        
        print(f"\n🚀 EXECUTANDO: {sistema['nome']}")
        print(f"📋 {sistema['descricao']}")
        print("-" * 50)
        
        try:
            resultado = subprocess.run([
                sys.executable, arquivo
            ], capture_output=False, text=True, cwd=os.getcwd())
            
            if resultado.returncode == 0:
                print(f"✅ {sistema['nome']} executado com sucesso!")
                return True
            else:
                print(f"⚠️ {sistema['nome']} finalizado com código {resultado.returncode}")
                return False
                
        except Exception as e:
            print(f"❌ Erro ao executar {sistema['nome']}: {e}")
            return False

    def executar_todos_sistemas(self) -> dict:
        """Executa todos os sistemas em sequência"""
        print("\n🎪 EXECUTANDO ANÁLISE COMPLETA - TODOS OS SISTEMAS")
        print("=" * 60)
        
        resultados = {}
        tempo_inicio = datetime.now()
        
        for tipo, sistema in self.sistemas_disponiveis.items():
            print(f"\n⏳ Iniciando {sistema['nome']}...")
            inicio_sistema = datetime.now()
            
            sucesso = self.executar_sistema(tipo)
            fim_sistema = datetime.now()
            tempo_sistema = (fim_sistema - inicio_sistema).total_seconds()
            
            resultados[tipo] = {
                'sucesso': sucesso,
                'tempo_execucao': tempo_sistema,
                'sistema': sistema['nome']
            }
            
            print(f"⏱️ Tempo: {tempo_sistema:.1f}s")
        
        tempo_total = (datetime.now() - tempo_inicio).total_seconds()
        
        # Relatório consolidado
        print(f"\n📊 RELATÓRIO CONSOLIDADO")
        print("=" * 35)
        print(f"⏱️ Tempo total: {tempo_total:.1f}s")
        
        sucessos = sum(1 for r in resultados.values() if r['sucesso'])
        total = len(resultados)
        
        print(f"✅ Sistemas executados: {sucessos}/{total}")
        
        for tipo, resultado in resultados.items():
            status = "✅" if resultado['sucesso'] else "❌"
            tempo = resultado['tempo_execucao']
            nome = resultado['sistema']
            print(f"   {status} {nome}: {tempo:.1f}s")
        
        return resultados

    def listar_arquivos_gerados(self) -> list:
        """Lista arquivos de relatório gerados hoje"""
        hoje = datetime.now().strftime("%Y%m%d")
        arquivos_encontrados = []
        
        # Padrões de arquivos dos sistemas
        padroes = [
            f"relatorio_inteligencia_preditiva_{hoje}*.txt",
            f"previsao_adaptativa_{hoje}*.txt", 
            f"relatorio_otimizacao_probabilistica_{hoje}*.txt"
        ]
        
        for arquivo in os.listdir('.'):
            if arquivo.endswith('.txt') and hoje in arquivo:
                if any(keyword in arquivo for keyword in ['inteligencia', 'previsao', 'otimizacao']):
                    tamanho = os.path.getsize(arquivo)
                    modificado = datetime.fromtimestamp(os.path.getmtime(arquivo))
                    
                    arquivos_encontrados.append({
                        'nome': arquivo,
                        'tamanho': tamanho,
                        'modificado': modificado,
                        'tipo': self._identificar_tipo_arquivo(arquivo)
                    })
        
        # Ordena por data de modificação (mais recente primeiro)
        arquivos_encontrados.sort(key=lambda x: x['modificado'], reverse=True)
        return arquivos_encontrados

    def _identificar_tipo_arquivo(self, nome_arquivo: str) -> str:
        """Identifica tipo do arquivo pela nomenclatura"""
        if 'inteligencia' in nome_arquivo:
            return '🧠 Inteligência Preditiva'
        elif 'previsao' in nome_arquivo:
            return '🔮 Previsão Adaptativa'
        elif 'otimizacao' in nome_arquivo:
            return '🎯 Otimização Probabilística'
        else:
            return '📄 Relatório'

    def comparar_resultados(self):
        """Compara resultados dos diferentes sistemas"""
        print("\n📊 COMPARAÇÃO DE RESULTADOS DOS SISTEMAS")
        print("=" * 45)
        
        arquivos = self.listar_arquivos_gerados()
        
        if not arquivos:
            print("❌ Nenhum relatório encontrado para hoje")
            print("💡 Execute os sistemas primeiro para gerar relatórios")
            return
        
        print(f"📁 {len(arquivos)} arquivo(s) encontrado(s):")
        print()
        
        for i, arquivo in enumerate(arquivos, 1):
            nome = arquivo['nome']
            tipo = arquivo['tipo']
            tamanho_kb = arquivo['tamanho'] / 1024
            modificado = arquivo['modificado'].strftime("%H:%M:%S")
            
            print(f"{i:2d}. {tipo}")
            print(f"    📄 {nome}")
            print(f"    💾 {tamanho_kb:.1f} KB | 🕒 {modificado}")
            print()
        
        # Análise rápida dos arquivos
        self._analisar_rapidamente_arquivos(arquivos)

    def _analisar_rapidamente_arquivos(self, arquivos: list):
        """Faz análise rápida dos conteúdos"""
        print("🔍 ANÁLISE RÁPIDA DOS CONTEÚDOS:")
        print("-" * 35)
        
        for arquivo in arquivos:
            nome = arquivo['nome']
            tipo = arquivo['tipo']
            
            try:
                with open(nome, 'r', encoding='utf-8') as f:
                    conteudo = f.read()
                
                # Conta linhas de combinações (não comentários)
                linhas = conteudo.split('\n')
                combinacoes = [l for l in linhas if l and not l.startswith('#') and ',' in l]
                
                print(f"{tipo}:")
                print(f"   🎲 {len(combinacoes):,} combinações geradas")
                
                # Busca por informações específicas
                if 'inteligencia' in nome:
                    if 'QUENTES:' in conteudo:
                        inicio = conteudo.find('QUENTES:') + 8
                        fim = conteudo.find('\n', inicio)
                        quentes = conteudo[inicio:fim].strip()
                        print(f"   🔥 Números quentes: {quentes}")
                
                elif 'previsao' in nome:
                    if 'Confiança global:' in conteudo:
                        inicio = conteudo.find('Confiança global:') + 17
                        fim = conteudo.find('\n', inicio)
                        confianca = conteudo[inicio:fim].strip()
                        print(f"   📊 Confiança: {confianca}")
                
                elif 'otimizacao' in nome:
                    if 'pares mais frequentes' in conteudo.lower():
                        print(f"   🔗 Análise de co-ocorrência completa")
                
                print()
                
            except Exception as e:
                print(f"   ⚠️ Erro ao analisar: {e}")
                print()

    def gerar_super_combinacao(self):
        """Gera combinações híbridas usando todos os sistemas"""
        print("\n🎯 GERADOR DE SUPER-COMBINAÇÕES HÍBRIDAS")
        print("=" * 50)
        
        # Verifica se há relatórios disponíveis
        arquivos = self.listar_arquivos_gerados()
        
        if len(arquivos) < 2:
            print("⚠️ Necessário pelo menos 2 sistemas executados")
            print("💡 Execute os sistemas primeiro para combinar resultados")
            return
        
        print(f"🧬 Combinando dados de {len(arquivos)} sistema(s)")
        
        # Extrai números recomendados de cada sistema
        numeros_recomendados = set()
        
        for arquivo in arquivos:
            nome = arquivo['nome']
            print(f"📊 Analisando {arquivo['tipo']}...")
            
            try:
                with open(nome, 'r', encoding='utf-8') as f:
                    conteudo = f.read()
                
                # Extrai primeiras 5 combinações de cada sistema
                linhas = conteudo.split('\n')
                combinacoes_sistema = []
                
                for linha in linhas:
                    if linha and not linha.startswith('#') and ',' in linha:
                        nums = [int(x) for x in linha.split(',')]
                        if len(nums) == 15:
                            combinacoes_sistema.append(nums)
                            if len(combinacoes_sistema) >= 5:
                                break
                
                # Adiciona números mais frequentes
                contador_nums = {}
                for combinacao in combinacoes_sistema:
                    for num in combinacao:
                        contador_nums[num] = contador_nums.get(num, 0) + 1
                
                # Pega top 8 números mais frequentes deste sistema
                nums_frequentes = sorted(contador_nums.items(), key=lambda x: x[1], reverse=True)[:8]
                for num, freq in nums_frequentes:
                    numeros_recomendados.add(num)
                
                print(f"   ✅ {len(nums_frequentes)} números extraídos")
                
            except Exception as e:
                print(f"   ❌ Erro ao processar: {e}")
        
        print(f"\n🎯 Total de números únicos coletados: {len(numeros_recomendados)}")
        print(f"📋 Números híbridos: {sorted(numeros_recomendados)}")
        
        # Gera combinações híbridas
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        nome_arquivo = f"super_combinacoes_hibridas_{timestamp}.txt"
        
        try:
            import random
            combinacoes_hibridas = []
            
            # Gera 1000 combinações usando números recomendados + aleatoriedade
            for _ in range(1000):
                combinacao = set()
                
                # 60% da combinação: números recomendados
                nums_recomendados_lista = list(numeros_recomendados)
                if len(nums_recomendados_lista) >= 9:
                    selecionados = random.sample(nums_recomendados_lista, 9)
                    combinacao.update(selecionados)
                
                # 40% restante: números aleatórios balanceados
                while len(combinacao) < 15:
                    num_aleatorio = random.randint(int(1), int(25))
                    combinacao.add(num_aleatorio)
                
                combinacao_ordenada = sorted(list(combinacao))
                if combinacao_ordenada not in combinacoes_hibridas:
                    combinacoes_hibridas.append(combinacao_ordenada)
            
            # Salva arquivo
            with open(nome_arquivo, 'w', encoding='utf-8') as f:
                f.write("🎯 SUPER-COMBINAÇÕES HÍBRIDAS\n")
                f.write("=" * 40 + "\n")
                f.write(f"Gerado em: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}\n")
                f.write(f"Sistemas utilizados: {len(arquivos)}\n")
                f.write(f"Números base híbridos: {sorted(numeros_recomendados)}\n")
                f.write(f"Total de combinações: {len(combinacoes_hibridas):,}\n\n")
                
                for combinacao in combinacoes_hibridas:
                    f.write(','.join(map(str, combinacao)) + '\n')
            
            print(f"\n✅ SUPER-COMBINAÇÕES GERADAS!")
            print(f"📄 Arquivo: {nome_arquivo}")
            print(f"🎲 {len(combinacoes_hibridas):,} combinações híbridas")
            
        except Exception as e:
            print(f"❌ Erro ao gerar super-combinações: {e}")

    def executar_menu_avancado(self):
        """Menu principal dos sistemas avançados"""
        while True:
            self.mostrar_menu_avancado()
            
            opcao = input("\nEscolha uma opção (0-6): ").strip()
            
            if opcao == "0":
                break
            
            elif opcao == "1":
                self.executar_sistema('inteligencia')
            
            elif opcao == "2":
                self.executar_sistema('adaptativa')
            
            elif opcao == "3":
                self.executar_sistema('probabilistica')
            
            elif opcao == "4":
                self.executar_todos_sistemas()
            
            elif opcao == "5":
                self.comparar_resultados()
            
            elif opcao == "6":
                self.gerar_super_combinacao()
            
            else:
                print("❌ Opção inválida")
            
            if opcao != "0":
                input("\n⏸️ Pressione ENTER para continuar...")


def main():
    """Função principal"""
    print("🚀 SISTEMA INTEGRADO DE ANÁLISE AVANÇADA")
    print("=" * 50)
    
    # Teste de conexão
    if not db_config.test_connection():
        print("❌ Erro na conexão com o banco")
        return
    
    sistema = SistemaIntegradoAvancado()
    
    try:
        sistema.executar_menu_avancado()
        print("\n👋 Sistema avançado finalizado!")
        
    except KeyboardInterrupt:
        print("\n⚠️ Operação interrompida pelo usuário")
    except Exception as e:
        print(f"❌ Erro inesperado: {e}")


if __name__ == "__main__":
    main()
