#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🎯 SISTEMA DE CONTROLE - GERADOR LOTOFÁCIL 16 NÚMEROS
Menu principal para todas as operações de geração de combinações

Autor: AR CALHAU  
Data: 24 de Agosto de 2025
"""

import os
import sys
from datetime import datetime
from database_config import db_config

# 🚀 SISTEMA DE OTIMIZAÇÃO DE BANCO
try:
    from database_optimizer import DatabaseOptimizer
    _db_optimizer = DatabaseOptimizer()
except ImportError:
    _db_optimizer = None


class ControleLotofacil16:
    """Sistema de controle principal"""
    
    def __init__(self):
        self.opcoes_menu = {
            "1": ("🧪 Gerar amostra de teste (10.000 combinações)", self.executar_teste),
            "2": ("🚀 Gerar TODAS as combinações (2.042.975)", self.executar_completo),
            "3": ("📊 Verificar status da tabela", self.verificar_status),
            "4": ("🔍 Consultar combinações existentes", self.consultar_combinacoes),
            "5": ("⚙️ Testar conexão com banco", self.testar_conexao),
            "6": ("🧹 Limpar tabela de teste", self.limpar_teste),
            "0": ("❌ Sair", self.sair)
        }
    
    def exibir_menu(self):
        """Exibe o menu principal"""
        print("\n" + "=" * 70)
        print("🎯 SISTEMA GERADOR LOTOFÁCIL 16 NÚMEROS")
        print("=" * 70)
        print("📋 Escolha uma opção:")
        print()
        
        for chave, (descricao, _) in self.opcoes_menu.items():
            print(f"   {chave} - {descricao}")
        
        print("\n" + "=" * 70)
    
    def executar_opcao(self, opcao: str):
        """Executa a opção escolhida"""
        if opcao in self.opcoes_menu:
            _, funcao = self.opcoes_menu[opcao]
            return funcao()
        else:
            print("❌ Opção inválida!")
            return True
    
    def executar_teste(self) -> bool:
        """Executa o modo teste"""
        print("\n🧪 MODO TESTE SELECIONADO")
        print("-" * 40)
        
        try:
            from gerar_combinacoes_16numeros_teste import GeradorTeste16
            
            print("Quantidade de combinações para teste:")
            print("  1 - 1.000 combinações (teste rápido)")
            print("  2 - 10.000 combinações (padrão)")
            print("  3 - 100.000 combinações (teste amplo)")
            print("  4 - Quantidade personalizada")
            
            opcao_qtde = input("\nEscolha (1-4): ").strip()
            
            if opcao_qtde == "1":
                quantidade = 1000
            elif opcao_qtde == "2":
                quantidade = 10000
            elif opcao_qtde == "3":
                quantidade = 100000
            elif opcao_qtde == "4":
                qtde_str = input("Digite a quantidade: ").strip()
                quantidade = int(qtde_str)
            else:
                print("❌ Opção inválida")
                return True
            
            if quantidade <= 0 or quantidade > 500000:
                print("❌ Quantidade deve estar entre 1 e 500.000")
                return True
            
            confirma = input(f"\n⚠️ Gerar {quantidade:,} combinações de teste? (s/n): ").lower()
            if confirma != 's':
                print("⏹️ Operação cancelada")
                return True
            
            print(f"\n🚀 Iniciando geração de {quantidade:,} combinações...")
            
            gerador_teste = GeradorTeste16()
            sucesso = gerador_teste.gerar_amostra_teste(quantidade)
            
            if sucesso:
                print("✅ Teste concluído com sucesso!")
                input("\nPressione ENTER para continuar...")
            else:
                print("❌ Erro no teste")
                input("\nPressione ENTER para continuar...")
                
        except ImportError:
            print("❌ Arquivo gerar_combinacoes_16numeros_teste.py não encontrado")
        except ValueError:
            print("❌ Quantidade inválida")
        except Exception as e:
            print(f"❌ Erro: {e}")
        
        return True
    
    def executar_completo(self) -> bool:
        """Executa a geração completa"""
        print("\n🚀 GERAÇÃO COMPLETA SELECIONADA")
        print("-" * 50)
        print("⚠️ Esta operação irá gerar TODAS as 2.042.975 combinações")
        print("   Tempo estimado: 2-4 horas dependendo do hardware")
        print("   Espaço em disco necessário: ~500MB")
        print()
        
        confirma1 = input("Deseja continuar? (s/n): ").lower()
        if confirma1 != 's':
            print("⏹️ Operação cancelada")
            return True
        
        print("\n📊 CONFIGURAÇÕES:")
        print("  • Total de combinações: 2.042.975")
        print("  • Processamento em lotes: 10.000 por vez")
        print("  • Progresso será exibido a cada lote")
        print("  • Índices serão criados automaticamente")
        
        confirma2 = input("\n⚠️ CONFIRMAÇÃO FINAL - Iniciar geração? (s/n): ").lower()
        if confirma2 != 's':
            print("⏹️ Operação cancelada")
            return True
        
        try:
            from gerar_combinacoes_16numeros import GeradorCombinacoes16
            
            print("\n🚀 INICIANDO GERAÇÃO COMPLETA...")
            print("=" * 60)
            
            gerador = GeradorCombinacoes16()
            sucesso = gerador.gerar_todas_combinacoes()
            
            if sucesso:
                print("\n🎉 GERAÇÃO COMPLETA FINALIZADA!")
                print("✅ Todas as 2.042.975 combinações foram geradas")
                input("\nPressione ENTER para continuar...")
            else:
                print("\n❌ Erro na geração completa")
                input("\nPressione ENTER para continuar...")
                
        except ImportError:
            print("❌ Arquivo gerar_combinacoes_16numeros.py não encontrado")
        except Exception as e:
            print(f"❌ Erro: {e}")
        
        return True
    
    def verificar_status(self) -> bool:
        """Verifica status das tabelas"""
        print("\n📊 VERIFICANDO STATUS DAS TABELAS")
        print("-" * 45)
        
        conn = None
        try:
            from gerar_combinacoes_16numeros import GeradorCombinacoes16
            
            gerador = GeradorCombinacoes16()
            conn = gerador.conectar_base()
            
            if not conn:
                print("❌ Erro na conexão")
                return True
            
            cursor = conn.cursor()
            
            # Verifica tabela principal
            try:
                cursor.execute("""
                SELECT COUNT_BIG(*) FROM [LOTOFACIL].[dbo].[COMBINACOES_LOTOFACIL16]
                """)
                count_principal = cursor.fetchone()[0]
                print(f"📊 COMBINACOES_LOTOFACIL16: {count_principal:,} registros")
                
                if count_principal > 0:
                    cursor.execute("""
                    SELECT MIN(SOMA), MAX(SOMA), AVG(CAST(SOMA as float))
                    FROM [LOTOFACIL].[dbo].[COMBINACOES_LOTOFACIL16]
                    """)
                    soma_min, soma_max, soma_avg = cursor.fetchone()
                    print(f"   • Soma: Min={soma_min}, Max={soma_max}, Média={soma_avg:.1f}")
                
            except:
                print("❌ Tabela COMBINACOES_LOTOFACIL16 não existe")
            
            # Verifica tabela de teste
            try:
                cursor.execute("""
                SELECT COUNT_BIG(*) FROM [LOTOFACIL].[dbo].[COMBINACOES_LOTOFACIL16_TESTE]
                """)
                count_teste = cursor.fetchone()[0]
                print(f"🧪 COMBINACOES_LOTOFACIL16_TESTE: {count_teste:,} registros")
                
            except:
                print("❌ Tabela COMBINACOES_LOTOFACIL16_TESTE não existe")
            
            # Verifica tabela original (15 números)
            try:
                cursor.execute("""
                SELECT COUNT_BIG(*) FROM [LOTOFACIL].[dbo].[COMBINACOES_LOTOFACIL]
                """)
                count_original = cursor.fetchone()[0]
                print(f"📊 COMBINACOES_LOTOFACIL (15 números): {count_original:,} registros")
                
            except:
                print("❌ Tabela COMBINACOES_LOTOFACIL não encontrada")
            
            print(f"\n💾 Status da conexão: ✅ Conectado")
            
        except Exception as e:
            print(f"❌ Erro ao verificar status: {e}")
        finally:
            if conn:
                conn.close()
        
        input("\nPressione ENTER para continuar...")
        return True
    
    def consultar_combinacoes(self) -> bool:
        """Consulta combinações existentes"""
        print("\n🔍 CONSULTANDO COMBINAÇÕES")
        print("-" * 35)
        
        tabelas = {
            "1": "COMBINACOES_LOTOFACIL16",
            "2": "COMBINACOES_LOTOFACIL16_TESTE", 
            "3": "COMBINACOES_LOTOFACIL"
        }
        
        print("Escolha a tabela:")
        print("  1 - Combinações 16 números (principal)")
        print("  2 - Combinações 16 números (teste)")
        print("  3 - Combinações 15 números (original)")
        
        opcao = input("\nTabela (1-3): ").strip()
        
        if opcao not in tabelas:
            print("❌ Opção inválida")
            return True
        
        nome_tabela = tabelas[opcao]
        
        conn = None
        try:
            from gerar_combinacoes_16numeros import GeradorCombinacoes16
            
            gerador = GeradorCombinacoes16()
            conn = gerador.conectar_base()
            
            cursor = conn.cursor()
            
            # Total de registros
        # SUGESTÃO: Use _db_optimizer.cached_query() para melhor performance
            cursor.execute(f"SELECT COUNT(*) FROM [LOTOFACIL].[dbo].[{nome_tabela}]")
            total = cursor.fetchone()[0]
            
            if total == 0:
                print("❌ Tabela vazia")
                return True
            
            print(f"\n📊 Total de registros: {total:,}")
            
            # Mostra primeiros 10 registros
            if "16" in nome_tabela:
                cursor.execute(f"""
                SELECT TOP 10 ID, N1, N2, N3, N4, N5, N6, N7, N8, N9, N10, N11, N12, N13, N14, N15, N16, SOMA, PARES
                FROM [LOTOFACIL].[dbo].[{nome_tabela}]
                ORDER BY ID
                """)
            else:
                cursor.execute(f"""
                SELECT TOP 10 ID, N1, N2, N3, N4, N5, N6, N7, N8, N9, N10, N11, N12, N13, N14, N15, SOMA, PARES
                FROM [LOTOFACIL].[dbo].[{nome_tabela}]
                ORDER BY ID
                """)
            
            print("\n🔍 Primeiros 10 registros:")
            for row in cursor.fetchall():
                if "16" in nome_tabela:
                    numeros = list(row[1:17])
                    soma = row[17]
                    pares = row[18]
                else:
                    numeros = list(row[1:16])
                    soma = row[16]
                    pares = row[17]
                
                print(f"   ID {row[0]:4d}: {numeros} | Soma: {soma:3d} | Pares: {pares}")
            
        except Exception as e:
            print(f"❌ Erro na consulta: {e}")
        finally:
            if conn:
                conn.close()
        
        input("\nPressione ENTER para continuar...")
        return True
    
    def testar_conexao(self) -> bool:
        """Testa conexão com o banco"""
        print("\n⚙️ TESTANDO CONEXÃO")
        print("-" * 25)
        
        if db_config.test_connection():
            print("✅ Conexão com banco: OK")
            print(f"🏢 Servidor: {db_config.server}")
            print(f"🗄️ Banco: {db_config.database}")
        else:
            print("❌ Erro na conexão com o banco")
            print("   Verifique as configurações em database_config.py")
        
        input("\nPressione ENTER para continuar...")
        return True
    
    def limpar_teste(self) -> bool:
        """Remove tabela de teste"""
        print("\n🧹 LIMPEZA DA TABELA DE TESTE")
        print("-" * 35)
        
        confirma = input("⚠️ Remover tabela COMBINACOES_LOTOFACIL16_TESTE? (s/n): ").lower()
        if confirma != 's':
            print("⏹️ Operação cancelada")
            return True
        
        conn = None
        try:
            from gerar_combinacoes_16numeros import GeradorCombinacoes16
            
            gerador = GeradorCombinacoes16()
            conn = gerador.conectar_base()
            
            cursor = conn.cursor()
            cursor.execute("""
            IF EXISTS (SELECT * FROM INFORMATION_SCHEMA.TABLES 
                      WHERE TABLE_SCHEMA = 'dbo' AND TABLE_NAME = 'COMBINACOES_LOTOFACIL16_TESTE')
                DROP TABLE [LOTOFACIL].[dbo].[COMBINACOES_LOTOFACIL16_TESTE]
            """)
            conn.commit()
            
            print("✅ Tabela de teste removida")
            
        except Exception as e:
            print(f"❌ Erro: {e}")
        finally:
            if conn:
                conn.close()
        
        input("\nPressione ENTER para continuar...")
        return True
    
    def sair(self) -> bool:
        """Sai do programa"""
        print("\n👋 Saindo do sistema...")
        return False
    
    def executar(self):
        """Loop principal do sistema"""
        while True:
            try:
                self.exibir_menu()
                opcao = input("Digite sua opção: ").strip()
                
                if not self.executar_opcao(opcao):
                    break
                    
            except KeyboardInterrupt:
                print("\n\n⏹️ Programa interrompido pelo usuário")
                break
            except Exception as e:
                print(f"\n❌ Erro inesperado: {e}")
                input("Pressione ENTER para continuar...")

def main():
    """Função principal"""
    try:
        print("🎯 SISTEMA LOTOFÁCIL 16 NÚMEROS")
        print(f"📅 Iniciado em: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
        
        controle = ControleLotofacil16()
        controle.executar()
        
    except Exception as e:
        print(f"❌ Erro crítico: {e}")
        input("Pressione ENTER para sair...")

if __name__ == "__main__":
    main()
