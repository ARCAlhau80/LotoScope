#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🔄 ATUALIZADOR MAIN MENU - SISTEMA LOTOFÁCIL

Sistema especializado para atualização da base de dados Lotofácil:
- Atualização de concursos na tabela resultados_int
- Execução de procedures SQL importantes  
- Cálculo de todos os campos estatísticos
- Sincronização com API oficial da Caixa

⚠️ COMPONENTE CRÍTICO: Não remover ou alterar sem conhecimento completo

Autor: AR CALHAU
Data: 25 de A        print("3️⃣  📊 Atualizar Range de Concursos")
        print("4️⃣  🚀 Atualização Completa Automática")
        print("5️⃣  🔧 Executar Procedures de Manutenção")
        print("6️⃣  🔄 Executar Procedures Completas (Especiais)")
        print("7️⃣  🔍 Verificar Procedures Importantes")
        print("8️⃣  📋 Gerar Relatório Completo")
        print("9️⃣  🚀 Sistema de Atualização Completa")
        print("0️⃣  🚪 Voltar ao Menu Principal")e 2025
"""

import os
import sys
import subprocess
import datetime
import time
from pathlib import Path

# Adicionar diretório base ao path para imports
_BASE_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(_BASE_DIR))
sys.path.insert(0, str(_BASE_DIR / 'interfaces'))
sys.path.insert(0, str(_BASE_DIR / 'utils'))

from menu_lotofacil import MenuLotofacil
from database_config import db_config

# 🚀 SISTEMA DE OTIMIZAÇÃO DE BANCO
try:
    from database_optimizer import DatabaseOptimizer
    _db_optimizer = DatabaseOptimizer()
except ImportError:
    _db_optimizer = None


class AtualizadorMainMenu:
    """
    Sistema especializado de atualização da base de dados Lotofácil
    """
    
    def __init__(self):
        self.diretorio_base = Path(__file__).parent
        self.menu_lotofacil = MenuLotofacil()
        self.procedures_executadas = False
    
    def verificar_conexao_base(self):
        """Verifica conexão com a base de dados"""
        print("🔗 VERIFICANDO CONEXÃO COM BASE DE DADOS...")
        print("-" * 50)
        
        if db_config.test_connection():
            print("✅ Conexão estabelecida com sucesso")
            
            # Verifica tabela principal
            if db_config.verificar_tabela_existe('Resultados_INT'):
                count = db_config.contar_registros('Resultados_INT')
                print(f"✅ Tabela Resultados_INT: {count:,} registros")
                
                # Obtém range de concursos
                query = "SELECT MIN(Concurso), MAX(Concurso) FROM Resultados_INT"
                resultado = db_config.execute_query(query)
                if resultado and resultado[0][0]:
                    min_conc, max_conc = resultado[0]
                    print(f"📊 Range: Concurso {min_conc} até {max_conc}")
                    return True
            else:
                print("❌ Tabela Resultados_INT não encontrada!")
                return False
        else:
            print("❌ Falha na conexão com a base de dados!")
            return False
    
    def obter_status_atualizacao(self):
        """Obtém status atual da base vs API"""
        print("📊 VERIFICANDO STATUS DE ATUALIZAÇÃO...")
        print("-" * 50)
        
        # Último concurso na base
        query = "SELECT MAX(Concurso) FROM Resultados_INT WHERE Concurso IS NOT NULL"
        resultado = db_config.execute_query(query)
        
        if resultado and resultado[0][0]:
            ultimo_base = resultado[0][0]
            print(f"📅 Último concurso na base: {ultimo_base}")
        else:
            ultimo_base = 0
            print("⚠️ Nenhum concurso encontrado na base")
        
        # Último concurso na API
        ultimo_api = self.menu_lotofacil.obter_ultimo_concurso_api()
        if ultimo_api > 0:
            print(f"🌐 Último concurso na API: {ultimo_api}")
            
            if ultimo_api > ultimo_base:
                diferenca = ultimo_api - ultimo_base
                print(f"📈 Concursos pendentes: {diferenca}")
                return {'base': ultimo_base, 'api': ultimo_api, 'pendentes': diferenca}
            else:
                print("✅ Base atualizada")
                return {'base': ultimo_base, 'api': ultimo_api, 'pendentes': 0}
        else:
            print("❌ Erro ao acessar API")
            return {'erro': 'Falha na API'}
    
    def atualizar_concurso_especifico(self):
        """Atualiza um concurso específico"""
        print("\n🎯 ATUALIZAÇÃO DE CONCURSO ESPECÍFICO")
        print("-" * 50)
        
        try:
            concurso = int(input("Digite o número do concurso: "))
            if concurso <= 0:
                print("❌ Número de concurso inválido")
                return
                
            print(f"🔄 Atualizando concurso {concurso}...")
            
            if self.menu_lotofacil.atualizar_concurso_individual(concurso):
                print(f"✅ Concurso {concurso} atualizado com sucesso!")
                
                # Executa procedures se necessário
                print("🔄 Executando procedures completas pós-atualização...")
                if self.executar_procedures_completas(concurso):
                    self.procedures_executadas = True
                    print("✅ Procedures completas executadas com sucesso")
                else:
                    print("⚠️ Erro nas procedures pós-atualização")
            else:
                print(f"❌ Erro ao atualizar concurso {concurso}")
                
        except ValueError:
            print("❌ Digite um número válido")
        except Exception as e:
            print(f"❌ Erro inesperado: {e}")
    
    def atualizar_range_concursos(self):
        """Atualiza um range de concursos"""
        print("\n📊 ATUALIZAÇÃO EM LOTE DE CONCURSOS")
        print("-" * 50)
        
        try:
            inicio = int(input("Concurso inicial: "))
            fim = int(input("Concurso final: "))
            
            if inicio <= 0 or fim <= 0 or inicio > fim:
                print("❌ Range inválido")
                return
                
            diferenca = fim - inicio + 1
            print(f"📈 Atualizando {diferenca} concursos ({inicio} a {fim})...")
            
            confirmacao = input("Confirma atualização? (s/N): ").strip().lower()
            if confirmacao != 's':
                print("⏹️ Operação cancelada")
                return
            
            stats = self.menu_lotofacil.atualizar_range_concursos(inicio, fim)
            
            print("\n📊 RESULTADO DA ATUALIZAÇÃO:")
            print(f"✅ Sucessos: {stats.get('sucessos', 0)}")
            print(f"❌ Falhas: {stats.get('falhas', 0)}")
            print(f"⏱️ Tempo total: {stats.get('tempo_total', 0):.2f}s")
            
            if stats.get('procedures_executadas'):
                self.procedures_executadas = True
                print("✅ Procedures completas pós-atualização executadas")
            else:
                # Se as procedures padrão não foram executadas, executa as completas
                print("🔄 Executando procedures completas adicionais...")
                ultimo_sucesso = stats.get('ultimo_concurso_sucesso', fim)
                if ultimo_sucesso > 0 and self.executar_procedures_completas(ultimo_sucesso):
                    self.procedures_executadas = True
                    print("✅ Procedures completas executadas com sucesso")
            
        except ValueError:
            print("❌ Digite números válidos")
        except Exception as e:
            print(f"❌ Erro inesperado: {e}")
    
    def atualizar_completo_automatico(self):
        """Atualização completa automática (base até API)"""
        print("\n🚀 ATUALIZAÇÃO COMPLETA AUTOMÁTICA")
        print("-" * 50)
        
        # Verifica status
        status = self.obter_status_atualizacao()
        if 'erro' in status:
            print("❌ Impossível prosseguir devido a erro na API")
            return
            
        pendentes = status.get('pendentes', 0)
        if pendentes == 0:
            print("✅ Base já está atualizada")
            return
            
        print(f"📈 {pendentes} concursos pendentes")
        print(f"🎯 Atualizando do concurso {status['base'] + 1} até {status['api']}")
        
        confirmacao = input("Confirma atualização completa? (s/N): ").strip().lower()
        if confirmacao != 's':
            print("⏹️ Operação cancelada")
            return
            
        print("\n🔄 INICIANDO ATUALIZAÇÃO COMPLETA...")
        inicio_processo = time.time()
        
        stats = self.menu_lotofacil.atualizar_completo()
        
        fim_processo = time.time()
        tempo_total = fim_processo - inicio_processo
        
        print(f"\n📊 RESULTADO DA ATUALIZAÇÃO COMPLETA:")
        if 'erro' not in stats:
            print(f"✅ Sucessos: {stats.get('sucessos', 0)}")
            print(f"❌ Falhas: {stats.get('falhas', 0)}")
            print(f"⏱️ Tempo total: {tempo_total:.2f}s")
            
            if stats.get('procedures_executadas'):
                self.procedures_executadas = True
                print("✅ Procedures completas pós-atualização executadas")
            else:
                # Executa procedures completas após atualização total
                print("🔄 Executando procedures completas finais...")
                ultimo_sucesso = stats.get('ultimo_concurso_sucesso', status['api'])
                if ultimo_sucesso > 0 and self.executar_procedures_completas(ultimo_sucesso):
                    self.procedures_executadas = True
                    print("✅ Procedures completas executadas com sucesso")
        else:
            print(f"❌ Erro: {stats['erro']}")
    
    def executar_procedures_manutencao(self):
        """Executa procedures de manutenção manualmente"""
        print("\n🔧 EXECUÇÃO MANUAL DE PROCEDURES")
        print("-" * 50)
        
        # Busca último concurso para executar procedures
        query = "SELECT MAX(Concurso) FROM Resultados_INT WHERE Concurso IS NOT NULL"
        resultado = db_config.execute_query(query)
        
        if not resultado or not resultado[0][0]:
            print("❌ Nenhum concurso encontrado na base")
            return
            
        ultimo_concurso = resultado[0][0]
        print(f"📊 Executando procedures com base no concurso {ultimo_concurso}")
        
        confirmacao = input("Confirma execução das procedures? (s/N): ").strip().lower()
        if confirmacao != 's':
            print("⏹️ Operação cancelada")
            return
        
        if self.executar_procedures_completas(ultimo_concurso):
            self.procedures_executadas = True
            print("✅ Todas as procedures executadas com sucesso")
        else:
            print("❌ Erro na execução das procedures")
    
    def executar_procedures_completas(self, ultimo_concurso: int) -> bool:
        """
        Executa procedures completas com configuração especial para AtualizaNumerosCiclos
        
        Args:
            ultimo_concurso: Número do último concurso atualizado
            
        Returns:
            bool: True se executou com sucesso
        """
        try:
            print(f"\n🔄 EXECUTANDO PROCEDURES COMPLETAS...")
            print(f"📊 Baseado no concurso: {ultimo_concurso}")
            
            with db_config.get_connection() as conn:
                cursor = conn.cursor()
                
                # 1. PROC_ATUALIZAR_COMBIN_10 (com trava anti-duplicação)
                print("🔄 Verificando COMBIN_10...")
                try:
                    cursor.execute("SELECT ISNULL(MAX(CONCURSO), 0) FROM COMBIN_10")
                    combin_conc = cursor.fetchone()[0]
                    cursor.execute("SELECT MAX(Concurso) FROM Resultados_INT")
                    result_conc = cursor.fetchone()[0]
                    if combin_conc >= result_conc:
                        print(f"✅ COMBIN_10 já atualizada (concurso {combin_conc}) — pulando")
                    else:
                        print(f"🔄 Executando PROC_ATUALIZAR_COMBIN_10 ({combin_conc} → {result_conc})...")
                        cursor.execute("EXEC PROC_ATUALIZAR_COMBIN_10")
                        conn.commit()
                        print("✅ PROC_ATUALIZAR_COMBIN_10 executada com sucesso")
                except Exception as e:
                    print(f"⚠️ Erro na PROC_ATUALIZAR_COMBIN_10: {e}")
                
                # 2. AtualizaNumerosCiclos (Execução múltipla conforme especificado)
                print("🔄 Executando AtualizaNumerosCiclos (configuração especial)...")
                try:
                    sql_atualiza_ciclos = """
                    DECLARE @return_value INT
                    DECLARE @i INT = 1
                    DECLARE @vezes INT = 1  -- quantidade de repetições

                    WHILE @i <= @vezes
                    BEGIN
                        EXEC @return_value = [dbo].[AtualizaNumerosCiclos]
                        -- opcional: mostrar progresso
                        PRINT CONCAT('Execução ', @i, ' concluída. Retorno = ', @return_value)

                        SET @i += 1
                    END
                    """
                    cursor.execute(sql_atualiza_ciclos)
                    conn.commit()
                    print("✅ AtualizaNumerosCiclos executada com configuração especial")
                except Exception as e:
                    print(f"⚠️ Erro na AtualizaNumerosCiclos: {e}")
                
                # 3. PROC_ATUALIZAR_QUINA
                print("🔄 Executando PROC_ATUALIZAR_QUINA...")
                try:
                    cursor.execute("EXEC PROC_ATUALIZAR_QUINA")
                    conn.commit()
                    print("✅ PROC_ATUALIZAR_QUINA executada com sucesso")
                except Exception as e:
                    print(f"⚠️ Erro na PROC_ATUALIZAR_QUINA: {e}")
                
                # 4. Atualizar campos QtdeRepetidos e RepetidosMesmaPosicao na COMBINACOES_LOTOFACIL
                print(f"🔄 Atualizando campos de repetidos na COMBINACOES_LOTOFACIL...")
                try:
                    self.menu_lotofacil.atualizar_campos_repetidos_combinacoes(ultimo_concurso, cursor, conn)
                    print("✅ Campos de repetidos atualizados na COMBINACOES_LOTOFACIL")
                except Exception as e:
                    print(f"⚠️ Erro ao atualizar campos repetidos: {e}")
                
                # Executar procedures de comparação com último concurso
                try:
                    cursor.execute("EXEC SP_AtualizarCamposComparacao @ConcursoNovo = ?", (ultimo_concurso,))
                    conn.commit()
                    print("✅ Campos de comparação atualizados na RESULTADOS_INT")
                except Exception as e:
                    print(f"⚠️ Erro ao executar SP_AtualizarCamposComparacao: {e}")
                
                try:
                    cursor.execute("EXEC SP_AtualizarCombinacoesComparacao @ConcursoReferencia = ?", (ultimo_concurso,))
                    conn.commit()
                    print("✅ Comparações atualizadas na COMBINACOES_LOTOFACIL")
                except Exception as e:
                    print(f"⚠️ Erro ao executar SP_AtualizarCombinacoesComparacao: {e}")
                
            print("✅ Todas as procedures completas executadas")
            return True
            
        except Exception as e:
            print(f"❌ Erro durante execução das procedures: {e}")
            return False
    
    def verificar_procedures_importantes(self):
        """Verifica se procedures importantes existem"""
        print("\n🔧 VERIFICANDO PROCEDURES IMPORTANTES")
        print("-" * 50)
        
        procedures = [
            'PROC_ATUALIZAR_COMBIN_10',
            'AtualizaNumerosCiclos', 
            'PROC_ATUALIZAR_QUINA',
            'SP_AtualizarCamposComparacao',
            'SP_AtualizarCombinacoesComparacao',
            'CalculaCamposApoio',
            'AtualizaCombinacoes'
        ]
        
        procedures_encontradas = 0
        
        for proc in procedures:
            query = """
            SELECT COUNT_BIG(*) FROM INFORMATION_SCHEMA.ROUTINES 
            WHERE ROUTINE_TYPE = 'PROCEDURE' AND ROUTINE_NAME = ?
            """
            resultado = db_config.execute_query(query, (proc,))
            
            if resultado and resultado[0][0] > 0:
                print(f"✅ {proc}: Disponível")
                procedures_encontradas += 1
            else:
                print(f"⚠️ {proc}: Não encontrada")
        
        print(f"\n📊 {procedures_encontradas}/{len(procedures)} procedures encontradas")
        
        if procedures_encontradas >= 3:
            print("✅ Procedures principais disponíveis")
        else:
            print("⚠️ Algumas procedures importantes estão ausentes")
    
    def gerar_relatorio_completo(self):
        """Gera relatório completo do estado da base"""
        print("\n📋 GERANDO RELATÓRIO COMPLETO...")
        print("-" * 50)
        
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        relatorio_file = self.diretorio_base / f"relatorio_atualizador_{timestamp}.txt"
        
        with open(relatorio_file, 'w', encoding='utf-8') as f:
            f.write("RELATÓRIO ATUALIZADOR MAIN MENU - SISTEMA LOTOFÁCIL\n")
            f.write("=" * 60 + "\n")
            f.write(f"Data/Hora: {datetime.datetime.now()}\n")
            f.write(f"Diretório: {self.diretorio_base}\n\n")
            
            # Status da conexão
            f.write("CONEXÃO COM BASE DE DADOS:\n")
            f.write("-" * 30 + "\n")
            
            if db_config.test_connection():
                f.write("✅ Status: Conectado\n")
                
                if db_config.verificar_tabela_existe('Resultados_INT'):
                    count = db_config.contar_registros('Resultados_INT')
                    f.write(f"✅ Resultados_INT: {count:,} registros\n")
                    
                    # Range de concursos
                    query = "SELECT MIN(Concurso), MAX(Concurso) FROM Resultados_INT"
                    resultado = db_config.execute_query(query)
                    if resultado and resultado[0][0]:
                        min_conc, max_conc = resultado[0]
                        f.write(f"📊 Range: {min_conc} - {max_conc}\n")
                else:
                    f.write("❌ Resultados_INT: Não encontrada\n")
            else:
                f.write("❌ Status: Desconectado\n")
            
            # Status vs API
            f.write("\nSTATUS DE ATUALIZAÇÃO:\n")
            f.write("-" * 30 + "\n")
            
            status = self.obter_status_atualizacao()
            if 'erro' not in status:
                f.write(f"Base: {status['base']}\n")
                f.write(f"API: {status['api']}\n")
                f.write(f"Pendentes: {status['pendentes']}\n")
            else:
                f.write("❌ Erro ao verificar status\n")
            
            f.write(f"\nRELATÓRIO GERADO EM: {timestamp}\n")
            f.write(f"Procedures executadas nesta sessão: {'Sim' if self.procedures_executadas else 'Não'}\n")
        
        print(f"📋 Relatório salvo: {relatorio_file.name}")
    
    def executar_procedures_finais(self):
        """Executa procedures completas como etapa final do processo"""
        print("🔄 EXECUTANDO PROCEDURES COMPLETAS FINAIS...")
        
        # Busca último concurso
        query = "SELECT MAX(Concurso) FROM Resultados_INT WHERE Concurso IS NOT NULL"
        resultado = db_config.execute_query(query)
        
        if not resultado or not resultado[0][0]:
            print("⚠️ Nenhum concurso encontrado - pulando procedures")
            return True
            
        ultimo_concurso = resultado[0][0]
        print(f"📊 Executando com base no concurso: {ultimo_concurso}")
        
        return self.executar_procedures_completas(ultimo_concurso)
    
    def executar_atualizacao_completa_sistema(self):
        """Executa verificação e atualização completa do sistema"""
        print("🚀 SISTEMA DE ATUALIZAÇÃO COMPLETA")
        print("=" * 60)
        
        etapas = [
            ("Verificação de Conexão", self.verificar_conexao_base),
            ("Status de Atualização", self.obter_status_atualizacao),
            ("Procedures Importantes", self.verificar_procedures_importantes),
            ("Atualização Automática", self.atualizar_completo_automatico),
            ("Procedures Completas Finais", self.executar_procedures_finais),
            ("Relatório Final", self.gerar_relatorio_completo)
        ]
        
        inicio = time.time()
        
        for i, (nome, funcao) in enumerate(etapas, 1):
            print(f"\n[{i}/{len(etapas)}] {nome}")
            print("-" * 40)
            
            try:
                resultado = funcao()
                if resultado is False:  # Se retornou False explicitamente
                    print(f"❌ {nome}: FALHOU - Interrompendo processo")
                    break
                else:
                    print(f"✅ {nome}: CONCLUÍDO")
            except Exception as e:
                print(f"❌ {nome}: ERRO - {e}")
                break
        
        fim = time.time()
        duracao = fim - inicio
        
        print("\n" + "=" * 60)
        print("🎉 PROCESSO DE ATUALIZAÇÃO FINALIZADO!")
        print(f"⏱️ Tempo total: {duracao:.2f} segundos")
        print(f"📅 Concluído em: {datetime.datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
        if self.procedures_executadas:
            print("✅ Procedures executadas durante o processo")
        print("=" * 60)

def menu_principal():
    """Menu principal do atualizador especializado"""
    atualizador = AtualizadorMainMenu()
    
    while True:
        print("\n🔄 ATUALIZADOR MAIN MENU - SISTEMA LOTOFÁCIL")
        print("=" * 60)
        print("ESPECIALIZADO EM ATUALIZAÇÃO DA BASE DE DADOS")
        print("=" * 60)
        print("1️⃣  � Verificar Status de Atualização")
        print("2️⃣  🎯 Atualizar Concurso Específico")
        print("3️⃣  📊 Atualizar Range de Concursos")
        print("4️⃣  🚀 Atualização Completa Automática")
        print("5️⃣  � Executar Procedures de Manutenção")
        print("6️⃣  🔍 Verificar Procedures Importantes")
        print("7️⃣  � Gerar Relatório Completo")
        print("8️⃣  🚀 Sistema de Atualização Completa")
        print("0️⃣  🚪 Voltar ao Menu Principal")
        print("=" * 60)
        
        escolha = input("🎯 Escolha uma opção (0-9): ").strip()
        
        if escolha == "1":
            atualizador.obter_status_atualizacao()
        elif escolha == "2":
            atualizador.atualizar_concurso_especifico()
        elif escolha == "3":
            atualizador.atualizar_range_concursos()
        elif escolha == "4":
            atualizador.atualizar_completo_automatico()
        elif escolha == "5":
            atualizador.executar_procedures_manutencao()
        elif escolha == "6":
            # Nova opção: Procedures completas especiais
            query = "SELECT MAX(Concurso) FROM Resultados_INT WHERE Concurso IS NOT NULL"
            resultado = db_config.execute_query(query)
            if resultado and resultado[0][0]:
                ultimo_concurso = resultado[0][0]
                print(f"\n🔄 EXECUTANDO PROCEDURES COMPLETAS ESPECIAIS")
                print(f"📊 Baseado no concurso: {ultimo_concurso}")
                confirmacao = input("Confirma execução? (s/N): ").strip().lower()
                if confirmacao == 's':
                    atualizador.executar_procedures_completas(ultimo_concurso)
            else:
                print("❌ Nenhum concurso encontrado na base")
        elif escolha == "7":
            atualizador.verificar_procedures_importantes()
        elif escolha == "8":
            atualizador.gerar_relatorio_completo()
        elif escolha == "9":
            atualizador.executar_atualizacao_completa_sistema()
        elif escolha == "0":
            print("\n👋 Voltando ao menu principal...")
            break
        else:
            print("❌ Opção inválida! Escolha entre 0-9.")
        
        if escolha != "0":
            input("\n⏸️ Pressione ENTER para continuar...")

def main():
    """Função principal"""
    try:
        print("🔥" * 70)
        print("🔄 ATUALIZADOR MAIN MENU - SISTEMA LOTOFÁCIL")
        print("🔥" * 70)
        print("⚠️  SISTEMA ESPECIALIZADO DE ATUALIZAÇÃO DA BASE DE DADOS")
        print("📊 Atualiza tabela resultados_int com dados da API oficial")
        print("🔧 Executa procedures SQL importantes automaticamente")
        print("🔥" * 70)
        print()
        
        menu_principal()
        
    except KeyboardInterrupt:
        print("\n\n⏹️ Atualização interrompida pelo usuário.")
    except Exception as e:
        print(f"\n❌ Erro inesperado: {e}")
        print("💡 Contate o suporte técnico se o problema persistir.")

if __name__ == "__main__":
    main()
