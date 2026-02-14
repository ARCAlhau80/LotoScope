#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🚀 FILTRO DE INTERSECÇÃO OTIMIZADO - LOTOFÁCIL

Sistema para filtrar combinações de 15 números que tenham
intersecção de 11-15 números com pelo menos uma combinação
de 20 números da tabela COMBINACOES_LOTOFACIL20_COMPLETO.

Performance otimizada com:
- Sets para intersecção O(1)
- Early termination 
- Processamento em lotes
- Monitoramento de progresso
- Multiprocessing opcional

Autor: AR CALHAU
Data: 10 de Setembro 2025
"""

import sys
from pathlib import Path
_BASE_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(_BASE_DIR))
sys.path.insert(0, str(_BASE_DIR / 'utils'))

import time
import os
from concurrent.futures import ProcessPoolExecutor, as_completed
from multiprocessing import cpu_count
import gc
from database_config import db_config

# 🚀 SISTEMA DE OTIMIZAÇÃO DE BANCO
try:
    from database_optimizer import DatabaseOptimizer
    _db_optimizer = DatabaseOptimizer()
except ImportError:
    _db_optimizer = None


class FiltroIntersecaoOtimizado:
    """
    Sistema otimizado para filtrar combinações por intersecção
    """
    
    def __init__(self):
        self.combo_15_data = []
        self.combo_20_sets = []
        self.resultados_validos = []
        self.total_processados = 0
        self.inicio_processo = None
        
    def carregar_dados(self):
        """
        Carrega dados das tabelas otimizadamente
        """
        print("🔄 CARREGANDO DADOS DAS TABELAS...")
        print("-" * 50)
        
        inicio = time.time()
        
        # Carregar combinações de 15 números
        print("📊 Carregando COMBINACOES_LOTOFACIL...")
        query_15 = "SELECT ID, Combinacao FROM COMBINACOES_LOTOFACIL ORDER BY ID"
        self.combo_15_data = db_config.execute_query(query_15)
        
        if not self.combo_15_data:
            print("❌ Erro ao carregar combinações de 15 números!")
            return False
        
        print(f"✅ Carregadas {len(self.combo_15_data):,} combinações de 15 números")
        
        # Carregar combinações de 20 números
        print("📊 Carregando COMBINACOES_LOTOFACIL20_COMPLETO...")
        query_20 = "SELECT Combinacao FROM COMBINACOES_LOTOFACIL20_COMPLETO"
        combo_20_data = db_config.execute_query(query_20)
        
        if not combo_20_data:
            print("❌ Erro ao carregar combinações de 20 números!")
            return False
            
        print(f"✅ Carregadas {len(combo_20_data):,} combinações de 20 números")
        
        # Converter combinações de 20 para sets (otimização)
        print("⚡ Convertendo combinações de 20 para sets...")
        self.combo_20_sets = []
        for combo_str in combo_20_data:
            numeros = set(map(int, combo_str[0].split(',')))
            self.combo_20_sets.append(numeros)
        
        fim = time.time()
        print(f"✅ Dados carregados em {fim - inicio:.2f} segundos")
        print(f"📊 Preparado para {len(self.combo_15_data):,} × {len(self.combo_20_sets):,} comparações")
        
        return True
    
    def processar_lote(self, lote_inicio, lote_fim):
        """
        Processa um lote de combinações de 15 números
        
        Args:
            lote_inicio: Índice inicial do lote
            lote_fim: Índice final do lote
            
        Returns:
            list: IDs das combinações válidas neste lote
        """
        validos_lote = []
        
        for i in range(lote_inicio, min(lote_fim, len(self.combo_15_data))):
            combo_15_id, combo_15_str = self.combo_15_data[i]
            combo_15_set = set(map(int, combo_15_str.split(',')))
            
            # Verificar intersecção com qualquer combinação de 20
            for combo_20_set in self.combo_20_sets:
                intersecao = len(combo_15_set & combo_20_set)
                
                if 11 <= intersecao <= 15:
                    validos_lote.append((combo_15_id, i, intersecao))
                    break  # Early termination - já encontrou uma válida
        
        return validos_lote
    
    def processar_sequencial(self, tamanho_lote=10000):
        """
        Processamento sequencial otimizado
        
        Args:
            tamanho_lote: Tamanho do lote para relatórios de progresso
        """
        print(f"\n🚀 INICIANDO PROCESSAMENTO SEQUENCIAL...")
        print(f"📊 Lotes de {tamanho_lote:,} combinações")
        print("-" * 50)
        
        self.inicio_processo = time.time()
        self.resultados_validos = []
        total_combinacoes = len(self.combo_15_data)
        
        for i in range(0, total_combinacoes, tamanho_lote):
            lote_fim = min(i + tamanho_lote, total_combinacoes)
            
            # Processar lote
            validos_lote = self.processar_lote(i, lote_fim)
            self.resultados_validos.extend(validos_lote)
            
            # Relatório de progresso
            self.total_processados = lote_fim
            self.imprimir_progresso(total_combinacoes)
            
            # Limpeza de memória ocasional
            if i % 50000 == 0 and i > 0:
                gc.collect()
        
        self.finalizar_processamento()
    
    def processar_paralelo(self, num_processos=None, tamanho_lote=50000):
        """
        Processamento paralelo otimizado
        
        Args:
            num_processos: Número de processos (None = automático)
            tamanho_lote: Tamanho de cada lote para paralelização
        """
        if num_processos is None:
            num_processos = max(1, cpu_count() - 1)
        
        print(f"\n🚀 INICIANDO PROCESSAMENTO PARALELO...")
        print(f"⚡ Usando {num_processos} processos")
        print(f"📊 Lotes de {tamanho_lote:,} combinações")
        print("-" * 50)
        
        self.inicio_processo = time.time()
        self.resultados_validos = []
        total_combinacoes = len(self.combo_15_data)
        
        # Criar lotes para paralelização
        lotes = []
        for i in range(0, total_combinacoes, tamanho_lote):
            lote_fim = min(i + tamanho_lote, total_combinacoes)
            lotes.append((i, lote_fim))
        
        print(f"📦 Criados {len(lotes)} lotes para processamento")
        
        # Processamento paralelo
        with ProcessPoolExecutor(max_workers=num_processos) as executor:
            # Submeter todos os lotes
            future_to_lote = {
                executor.submit(self.processar_lote_worker, inicio, fim): (inicio, fim)
                for inicio, fim in lotes
            }
            
            # Coletar resultados conforme completam
            lotes_processados = 0
            for future in as_completed(future_to_lote):
                inicio, fim = future_to_lote[future]
                
                try:
                    validos_lote = future.result()
                    self.resultados_validos.extend(validos_lote)
                    
                    lotes_processados += 1
                    self.total_processados = lotes_processados * tamanho_lote
                    
                    # Relatório de progresso
                    if lotes_processados % max(1, len(lotes) // 10) == 0:
                        self.imprimir_progresso(total_combinacoes)
                    
                except Exception as exc:
                    print(f"❌ Erro no lote {inicio}-{fim}: {exc}")
        
        self.finalizar_processamento()
    
    def processar_lote_worker(self, lote_inicio, lote_fim):
        """
        Worker function para processamento paralelo
        (Versão independente para multiprocessing)
        """
        # Reconectar ao banco no processo filho
        validos_lote = []
        
        # Carregar dados localmente no processo
        query_15 = f"SELECT ID, Combinacao FROM COMBINACOES_LOTOFACIL WHERE ID BETWEEN (SELECT MIN(ID) FROM (SELECT ID, ROW_NUMBER() OVER (ORDER BY ID) as rn FROM COMBINACOES_LOTOFACIL) t WHERE rn = {lote_inicio + 1}) AND (SELECT MIN(ID) FROM (SELECT ID, ROW_NUMBER() OVER (ORDER BY ID) as rn FROM COMBINACOES_LOTOFACIL) t WHERE rn = {lote_fim})"
        
        combo_15_lote = db_config.execute_query(query_15)
        
        query_20 = "SELECT Combinacao FROM COMBINACOES_LOTOFACIL20_COMPLETO"
        combo_20_data = db_config.execute_query(query_20)
        
        # Converter para sets
        combo_20_sets = [set(map(int, combo[0].split(','))) for combo in combo_20_data]
        
        # Processar
        for combo_15_id, combo_15_str in combo_15_lote:
            combo_15_set = set(map(int, combo_15_str.split(',')))
            
            for combo_20_set in combo_20_sets:
                intersecao = len(combo_15_set & combo_20_set)
                
                if 11 <= intersecao <= 15:
                    validos_lote.append((combo_15_id, intersecao))
                    break
        
        return validos_lote
    
    def imprimir_progresso(self, total_combinacoes):
        """
        Imprime progresso do processamento
        """
        if not self.inicio_processo:
            return
            
        tempo_decorrido = time.time() - self.inicio_processo
        progresso_pct = (self.total_processados / total_combinacoes) * 100
        
        # Estimativa de tempo restante
        if progresso_pct > 0:
            tempo_estimado_total = tempo_decorrido * (100 / progresso_pct)
            tempo_restante = tempo_estimado_total - tempo_decorrido
        else:
            tempo_restante = 0
        
        print(f"⏱️ Progresso: {self.total_processados:,}/{total_combinacoes:,} ({progresso_pct:.1f}%) | "
              f"Válidas: {len(self.resultados_validos):,} | "
              f"Tempo: {tempo_decorrido:.0f}s | "
              f"Restante: ~{tempo_restante:.0f}s")
    
    def finalizar_processamento(self):
        """
        Finaliza o processamento e exibe estatísticas
        """
        if not self.inicio_processo:
            return
            
        tempo_total = time.time() - self.inicio_processo
        total_combinacoes = len(self.combo_15_data)
        
        print("\n" + "=" * 60)
        print("🎉 PROCESSAMENTO CONCLUÍDO!")
        print("=" * 60)
        print(f"📊 Total processado: {total_combinacoes:,} combinações")
        print(f"✅ Combinações válidas: {len(self.resultados_validos):,}")
        print(f"📉 Taxa de aprovação: {(len(self.resultados_validos) / total_combinacoes) * 100:.2f}%")
        print(f"⏱️ Tempo total: {tempo_total:.2f} segundos")
        print(f"🚀 Velocidade: {total_combinacoes / tempo_total:,.0f} combinações/segundo")
        print("=" * 60)
    
    def salvar_resultados(self, nome_arquivo=None):
        """
        Salva resultados em arquivo
        
        Args:
            nome_arquivo: Nome do arquivo (opcional)
        """
        if not self.resultados_validos:
            print("⚠️ Nenhum resultado para salvar!")
            return False
        
        if nome_arquivo is None:
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            nome_arquivo = f"combinacoes_filtradas_{timestamp}.txt"
        
        caminho_arquivo = Path(__file__).parent / nome_arquivo
        
        print(f"\n💾 Salvando resultados em: {nome_arquivo}")
        
        try:
            with open(caminho_arquivo, 'w', encoding='utf-8') as f:
                f.write("COMBINAÇÕES DE 15 NÚMEROS FILTRADAS POR INTERSECÇÃO\n")
                f.write("=" * 60 + "\n")
                f.write(f"Total de combinações válidas: {len(self.resultados_validos):,}\n")
                f.write(f"Critério: 11-15 números em comum com pelo menos uma combinação de 20\n")
                f.write("-" * 60 + "\n")
                
                for resultado in self.resultados_validos:
                    if len(resultado) == 3:  # (id, indice, intersecao)
                        combo_id, indice, intersecao = resultado
                        f.write(f"ID: {combo_id}, Intersecção: {intersecao}\n")
                    else:  # (id, intersecao)
                        combo_id, intersecao = resultado
                        f.write(f"ID: {combo_id}, Intersecção: {intersecao}\n")
            
            print(f"✅ Arquivo salvo: {caminho_arquivo}")
            return True
            
        except Exception as e:
            print(f"❌ Erro ao salvar arquivo: {e}")
            return False
    
    def executar_filtro_completo(self, modo="sequencial", salvar=True):
        """
        Executa o filtro completo
        
        Args:
            modo: "sequencial" ou "paralelo"
            salvar: Se deve salvar os resultados
        """
        print("🚀" * 25)
        print("🚀 FILTRO DE INTERSECÇÃO OTIMIZADO - LOTOFÁCIL")
        print("🚀" * 25)
        print(f"🎯 Modo: {modo.upper()}")
        print("📊 Filtro: Combinações de 15 com 11-15 números em comum")
        print("🔍 Com pelo menos uma combinação de 20 números")
        print("🚀" * 25)
        
        # Carregar dados
        if not self.carregar_dados():
            print("❌ Falha ao carregar dados!")
            return False
        
        # Processar
        if modo.lower() == "paralelo":
            self.processar_paralelo()
        else:
            self.processar_sequencial()
        
        # Salvar resultados
        if salvar and self.resultados_validos:
            self.salvar_resultados()
        
        return True

def menu_principal():
    """
    Menu principal do sistema
    """
    filtro = FiltroIntersecaoOtimizado()
    
    while True:
        print("\n🚀 FILTRO DE INTERSECÇÃO - MENU PRINCIPAL")
        print("=" * 50)
        print("1️⃣  🔄 Executar Filtro Sequencial")
        print("2️⃣  ⚡ Executar Filtro Paralelo")
        print("3️⃣  🧪 Teste Rápido (1000 combinações)")
        print("4️⃣  📊 Status das Tabelas")
        print("0️⃣  🚪 Sair")
        print("=" * 50)
        
        escolha = input("🎯 Escolha uma opção (0-4): ").strip()
        
        if escolha == "1":
            print("🔄 Iniciando processamento sequencial...")
            filtro.executar_filtro_completo("sequencial")
        
        elif escolha == "2":
            print("⚡ Iniciando processamento paralelo...")
            filtro.executar_filtro_completo("paralelo")
        
        elif escolha == "3":
            print("🧪 Executando teste rápido...")
            # Implementar teste com subset pequeno
            print("⚠️ Função de teste ainda não implementada")
        
        elif escolha == "4":
            print("📊 Verificando status das tabelas...")
            if db_config.test_connection():
                count_15 = db_config.contar_registros('COMBINACOES_LOTOFACIL')
                count_20 = db_config.contar_registros('COMBINACOES_LOTOFACIL20_COMPLETO')
                print(f"✅ COMBINACOES_LOTOFACIL: {count_15:,} registros")
                print(f"✅ COMBINACOES_LOTOFACIL20_COMPLETO: {count_20:,} registros")
            else:
                print("❌ Erro de conexão com banco de dados")
        
        elif escolha == "0":
            print("👋 Encerrando sistema...")
            break
        
        else:
            print("❌ Opção inválida!")
        
        if escolha != "0":
            input("\n⏸️ Pressione ENTER para continuar...")

def main():
    """
    Função principal
    """
    try:
        menu_principal()
    except KeyboardInterrupt:
        print("\n\n⏹️ Operação interrompida pelo usuário.")
    except Exception as e:
        print(f"\n❌ Erro inesperado: {e}")

if __name__ == "__main__":
    main()
