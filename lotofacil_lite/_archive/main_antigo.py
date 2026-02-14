#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🏠 MENU PRINCIPAL - LOTOFÁCIL LITE
Sistema enxuto para atualização da base e geração de combinações
Autor: AR CALHAU
Data: 04 de Agosto de 2025
"""

import sys
import os
from datetime import datetime

# Importa módulos do sistema
from database_config import db_config

# 🚀 SISTEMA DE OTIMIZAÇÃO DE BANCO
try:
    from database_optimizer import DatabaseOptimizer
    _db_optimizer = DatabaseOptimizer()
except ImportError:
    _db_optimizer = None

from menu_lotofacil import MenuLotofacil
from lotofacil_generator import LotofacilGenerator
from teste_temporal import TesteTemporalInteligente
from inteligencia_primos_fibonacci import InteligenciaPrimosFibonacci
from gerador_hibrido_completo import GeradorHibridoCompleto

class MainMenu:
    """Menu principal do sistema Lotofácil Lite"""
    
    def __init__(self):
        self.menu_lotofacil = MenuLotofacil()
        self.generator = LotofacilGenerator()
        
    def exibir_menu_principal(self):
        """Exibe o menu principal"""
        print("\n" + "=" * 60)
        print("🎯 LOTOFÁCIL LITE - SISTEMA ENXUTO")
        print("=" * 60)
        print("📊 ATUALIZAÇÃO DA BASE:")
        print("   1 - Testar conexão com banco de dados")
        print("   2 - Obter último concurso da API")
        print("   3 - Atualizar concurso específico")
        print("   4 - Atualização completa (recomendado)")
        print("   5 - Atualizar range de concursos")
        
        print("\n🎲 GERAÇÃO DE COMBINAÇÕES:")
        print("   6 - Combinações aleatórias")
        print("   7 - Combinações por frequência")
        print("   8 - Combinações por ciclos")
        print("   9 - Combinações balanceadas")
        print("  10 - Combinações por padrões")
        print("  11 - Expandir quina para combinações")
        print("  12 - Configurar sistema de intuição")
        print("  13 - Gerar mix personalizado")
        print("  14 - 🎯 ANÁLISE POSICIONAL AVANÇADA (NOVO!)")
        print("  15 - 🧠 POSICIONAL INTELIGENTE + CICLOS (NOVO!)")
        print("  16 - 🔢🌀 GERADOR PRIMOS + FIBONACCI (NOVO!)")
        print("  17 - 🌟 GERADOR HÍBRIDO COMPLETO (NOVO!)")
        
        print("\n📊 ANÁLISE & VALIDAÇÃO:")
        print("  18 - 📊 BACKTESTING POSICIONAL")
        print("  19 - 🕰️ TESTES TEMPORAIS & VALIDAÇÃO (NOVO!)")
        
        print("\n⚙️ SISTEMA:")
        print("  20 - Status do sistema")
        print("  21 - Limpar cache")
        print("   0 - Sair")
        print("=" * 60)
    
    def opcao_1_testar_conexao(self):
        """Testa conexão com banco de dados"""
        print("\n🔍 TESTANDO CONEXÃO COM BANCO DE DADOS")
        print("-" * 40)
        
        if db_config.test_connection():
            print("✅ Conexão estabelecida com sucesso!")
            
            # Testa algumas consultas básicas
            print("\n📊 Testando consultas básicas...")
            
            # Conta total de registros
            resultado = db_config.execute_query("SELECT COUNT_BIG(*) FROM Resultados_INT")
            if resultado:
                total = resultado[0][0]
                print(f"   • Total de concursos na base: {total}")
            
            # Último concurso
            resultado = db_config.execute_query("SELECT MAX(Concurso) FROM Resultados_INT")
            if resultado and resultado[0][0]:
                ultimo = resultado[0][0]
                print(f"   • Último concurso: {ultimo}")
            
            print("✅ Sistema pronto para uso!")
        else:
            print("❌ Falha na conexão!")
            print("📝 Verifique:")
            print("   • Servidor SQL Server está rodando")
            print("   • Nome do banco está correto")
            print("   • Credenciais de acesso")
            print("   • String de conexão em database_config.py")
    
    def opcao_2_ultimo_concurso_api(self):
        """Obtém último concurso da API"""
        print("\n🌐 CONSULTANDO ÚLTIMO CONCURSO NA API")
        print("-" * 40)
        
        ultimo = self.menu_lotofacil.obter_ultimo_concurso_api()
        if ultimo > 0:
            print(f"🎯 Último concurso disponível: {ultimo}")
            
            # Compara com a base
            resultado = db_config.execute_query("SELECT MAX(Concurso) FROM Resultados_INT")
            if resultado and resultado[0][0]:
                ultimo_base = resultado[0][0]
                diferenca = ultimo - ultimo_base
                print(f"📊 Último concurso na base: {ultimo_base}")
                if diferenca > 0:
                    print(f"⚠️ Base está {diferenca} concurso(s) atrasada")
                    print("💡 Use a opção 4 para atualização completa")
                else:
                    print("✅ Base está atualizada!")
        else:
            print("❌ Erro ao consultar API da Caixa")
    
    def opcao_3_atualizar_especifico(self):
        """Atualiza concurso específico"""
        print("\n📊 ATUALIZAR CONCURSO ESPECÍFICO")
        print("-" * 40)
        
        try:
            concurso = int(input("Digite o número do concurso: ").strip())
            
            if concurso <= 0:
                print("❌ Número de concurso inválido")
                return
            
            print(f"\n🔄 Atualizando concurso {concurso}...")
            sucesso = self.menu_lotofacil.atualizar_concurso_individual(concurso)
            
            if sucesso:
                print(f"✅ Concurso {concurso} atualizado com sucesso!")
            else:
                print(f"❌ Erro ao atualizar concurso {concurso}")
                
        except ValueError:
            print("❌ Digite um número válido")
        except Exception as e:
            print(f"❌ Erro: {e}")
    
    def opcao_4_atualizacao_completa(self):
        """Executa atualização completa"""
        print("\n🚀 ATUALIZAÇÃO COMPLETA DA BASE")
        print("-" * 40)
        
        confirma = input("Confirma a atualização completa? (s/N): ").strip().lower()
        if confirma != 's':
            print("❌ Operação cancelada")
            return
        
        print("\n🔄 Iniciando atualização completa...")
        resultado = self.menu_lotofacil.atualizar_completo()
        
        if 'erro' in resultado:
            print(f"❌ Erro: {resultado['erro']}")
        elif 'status' in resultado and resultado['status'] == 'atualizada':
            print("✅ Base já estava atualizada!")
        else:
            print("\n📊 RESULTADO DA ATUALIZAÇÃO:")
            print(f"   • Total processados: {resultado.get('total_processados', 0)}")
            print(f"   • Sucessos: {resultado.get('sucessos', 0)}")
            print(f"   • Falhas: {resultado.get('falhas', 0)}")
            print(f"   • Tempo total: {resultado.get('tempo_total', 0):.2f}s")
    
    def opcao_5_atualizar_range(self):
        """Atualiza range de concursos"""
        print("\n📈 ATUALIZAR RANGE DE CONCURSOS")
        print("-" * 40)
        
        try:
            inicio = int(input("Concurso inicial: ").strip())
            fim = int(input("Concurso final: ").strip())
            
            if inicio <= 0 or fim <= 0 or inicio > fim:
                print("❌ Range inválido")
                return
            
            total = fim - inicio + 1
            confirma = input(f"Confirma atualização de {total} concursos ({inicio}-{fim})? (s/N): ").strip().lower()
            if confirma != 's':
                print("❌ Operação cancelada")
                return
            
            resultado = self.menu_lotofacil.atualizar_range_concursos(inicio, fim)
            print("✅ Atualização concluída!")
            
        except ValueError:
            print("❌ Digite números válidos")
        except Exception as e:
            print(f"❌ Erro: {e}")
    
    def opcao_6_combinacoes_aleatorias(self):
        """Gera combinações aleatórias"""
        print("\n🎲 COMBINAÇÕES ALEATÓRIAS")
        print("-" * 40)
        
        try:
            quantidade = int(input("Quantas combinações gerar? (1-50): ").strip())
            if not 1 <= quantidade <= 50:
                print("❌ Quantidade deve ser entre 1 e 50")
                return
            
            combinacoes = self.generator.generate_random_combinations(quantidade)
            self._exibir_combinacoes(combinacoes, "ALEATÓRIAS")
            self._oferecer_salvar(combinacoes)
            
        except ValueError:
            print("❌ Digite um número válido")
    
    def opcao_7_combinacoes_frequencia(self):
        """Gera combinações por frequência"""
        print("\n📊 COMBINAÇÕES POR FREQUÊNCIA")
        print("-" * 40)
        
        try:
            quantidade = int(input("Quantas combinações gerar? (1-50): ").strip())
            if not 1 <= quantidade <= 50:
                print("❌ Quantidade deve ser entre 1 e 50")
                return
            
            combinacoes = self.generator.generate_frequency_based_combinations(quantidade)
            self._exibir_combinacoes(combinacoes, "POR FREQUÊNCIA")
            self._oferecer_salvar(combinacoes)
            
        except ValueError:
            print("❌ Digite um número válido")
    
    def opcao_8_combinacoes_ciclos(self):
        """Gera combinações por ciclos"""
        print("\n🔄 COMBINAÇÕES POR CICLOS")
        print("-" * 40)
        
        try:
            quantidade = int(input("Quantas combinações gerar? (1-50): ").strip())
            if not 1 <= quantidade <= 50:
                print("❌ Quantidade deve ser entre 1 e 50")
                return
            
            combinacoes = self.generator.generate_cycles_based_combinations(quantidade)
            self._exibir_combinacoes(combinacoes, "POR CICLOS")
            self._oferecer_salvar(combinacoes)
            
        except ValueError:
            print("❌ Digite um número válido")
    
    def opcao_9_combinacoes_balanceadas(self):
        """Gera combinações balanceadas"""
        print("\n⚖️ COMBINAÇÕES BALANCEADAS")
        print("-" * 40)
        
        try:
            quantidade = int(input("Quantas combinações gerar? (1-50): ").strip())
            if not 1 <= quantidade <= 50:
                print("❌ Quantidade deve ser entre 1 e 50")
                return
            
            combinacoes = self.generator.generate_balanced_combinations(quantidade)
            self._exibir_combinacoes(combinacoes, "BALANCEADAS")
            self._oferecer_salvar(combinacoes)
            
        except ValueError:
            print("❌ Digite um número válido")
    
    def opcao_10_combinacoes_padroes(self):
        """Gera combinações por padrões"""
        print("\n🔍 COMBINAÇÕES POR PADRÕES")
        print("-" * 40)
        
        try:
            quantidade = int(input("Quantas combinações gerar? (1-50): ").strip())
            if not 1 <= quantidade <= 50:
                print("❌ Quantidade deve ser entre 1 e 50")
                return
            
            combinacoes = self.generator.generate_pattern_combinations(quantidade)
            self._exibir_combinacoes(combinacoes, "POR PADRÕES")
            self._oferecer_salvar(combinacoes)
            
        except ValueError:
            print("❌ Digite um número válido")
    
    def opcao_11_expandir_quina(self):
        """Expande quina para combinações"""
        print("\n🔧 EXPANDIR QUINA PARA COMBINAÇÕES")
        print("-" * 40)
        
        try:
            print("Digite 5 números da quina (separados por espaço):")
            entrada = input("Ex: 3 7 12 18 23: ").strip()
            
            numeros = [int(x) for x in entrada.split()]
            
            if len(numeros) != 5:
                print("❌ Digite exatamente 5 números")
                return
            
            if not all(1 <= n <= 25 for n in numeros):
                print("❌ Números devem estar entre 1 e 25")
                return
            
            if len(set(numeros)) != 5:
                print("❌ Números não podem se repetir")
                return
            
            quantidade = int(input("Quantas combinações gerar dessa quina? (1-20): ").strip())
            if not 1 <= quantidade <= 20:
                print("❌ Quantidade deve ser entre 1 e 20")
                return
            
            combinacoes = self.generator.expand_quina_to_combination(numeros, quantidade)
            self._exibir_combinacoes(combinacoes, f"EXPANDIDAS DA QUINA {numeros}")
            self._oferecer_salvar(combinacoes)
            
        except ValueError:
            print("❌ Digite números válidos")
        except Exception as e:
            print(f"❌ Erro: {e}")
    
    def opcao_12_configurar_intuicao(self):
        """Configura sistema de intuição"""
        print("\n🧠 CONFIGURAR SISTEMA DE INTUIÇÃO")
        print("-" * 40)
        
        try:
            print("NÚMEROS OBRIGATÓRIOS (devem estar na combinação):")
            entrada_obrig = input("Digite os números separados por espaço (Enter para nenhum): ").strip()
            
            obrigatorios = []
            if entrada_obrig:
                obrigatorios = [int(x) for x in entrada_obrig.split()]
                if not all(1 <= n <= 25 for n in obrigatorios):
                    print("❌ Números devem estar entre 1 e 25")
                    return
                if len(set(obrigatorios)) != len(obrigatorios):
                    print("❌ Números não podem se repetir")
                    return
                if len(obrigatorios) > 15:
                    print("❌ Máximo 15 números obrigatórios")
                    return
            
            print("\nNÚMEROS PROIBIDOS (não podem estar na combinação):")
            entrada_proib = input("Digite os números separados por espaço (Enter para nenhum): ").strip()
            
            proibidos = []
            if entrada_proib:
                proibidos = [int(x) for x in entrada_proib.split()]
                if not all(1 <= n <= 25 for n in proibidos):
                    print("❌ Números devem estar entre 1 e 25")
                    return
                if len(set(proibidos)) != len(proibidos):
                    print("❌ Números não podem se repetir")
                    return
            
            # Verifica conflitos
            conflito = set(obrigatorios) & set(proibidos)
            if conflito:
                print(f"❌ Conflito: números {conflito} são obrigatórios E proibidos")
                return
            
            # Configura no gerador
            self.generator.configure_intuition_numbers(obrigatorios, proibidos)
            
            print("\n✅ INTUIÇÃO CONFIGURADA:")
            if obrigatorios:
                print(f"   🎯 Obrigatórios: {sorted(obrigatorios)}")
            if proibidos:
                print(f"   🚫 Proibidos: {sorted(proibidos)}")
            if not obrigatorios and not proibidos:
                print("   🔄 Sistema resetado (sem restrições)")
            
        except ValueError:
            print("❌ Digite números válidos")
        except Exception as e:
            print(f"❌ Erro: {e}")
    
    def opcao_13_mix_personalizado(self):
        """Gera mix personalizado de combinações"""
        print("\n🎨 MIX PERSONALIZADO DE COMBINAÇÕES")
        print("-" * 40)
        
        try:
            print("Escolha quantas combinações de cada tipo:")
            aleatorias = int(input("Aleatórias (0-20): ").strip() or "0")
            frequencia = int(input("Por frequência (0-20): ").strip() or "0")
            ciclos = int(input("Por ciclos (0-20): ").strip() or "0")
            balanceadas = int(input("Balanceadas (0-20): ").strip() or "0")
            padroes = int(input("Por padrões (0-20): ").strip() or "0")
            
            total = aleatorias + frequencia + ciclos + balanceadas + padroes
            
            if total == 0:
                print("❌ Selecione pelo menos um tipo")
                return
            
            if total > 100:
                print("❌ Total máximo: 100 combinações")
                return
            
            print(f"\n🔄 Gerando {total} combinações personalizadas...")
            
            todas_combinacoes = []
            
            if aleatorias > 0:
                comb = self.generator.generate_random_combinations(aleatorias)
                todas_combinacoes.extend(comb)
                print(f"✅ {len(comb)} aleatórias geradas")
            
            if frequencia > 0:
                comb = self.generator.generate_frequency_based_combinations(frequencia)
                todas_combinacoes.extend(comb)
                print(f"✅ {len(comb)} por frequência geradas")
            
            if ciclos > 0:
                comb = self.generator.generate_cycles_based_combinations(ciclos)
                todas_combinacoes.extend(comb)
                print(f"✅ {len(comb)} por ciclos geradas")
            
            if balanceadas > 0:
                comb = self.generator.generate_balanced_combinations(balanceadas)
                todas_combinacoes.extend(comb)
                print(f"✅ {len(comb)} balanceadas geradas")
            
            if padroes > 0:
                comb = self.generator.generate_pattern_combinations(padroes)
                todas_combinacoes.extend(comb)
                print(f"✅ {len(comb)} por padrões geradas")
            
            self._exibir_combinacoes(todas_combinacoes, "MIX PERSONALIZADO")
            self._oferecer_salvar(todas_combinacoes)
            
        except ValueError:
            print("❌ Digite números válidos")
        except Exception as e:
            print(f"❌ Erro: {e}")
    
    def opcao_14_analise_posicional(self):
        """Gera combinações usando análise posicional avançada"""
        print("\n🎯 ANÁLISE POSICIONAL AVANÇADA")
        print("-" * 50)
        print("🔬 Sistema sofisticado que analisa cada posição (N1 até N15)")
        print("📊 Usa algoritmos acadêmicos para ranquear números por posição")
        print("🎲 Considera correlações causais entre posições")
        print("⏱️ Analisa 4 janelas temporais: geral, 30, 15 e 5 últimos sorteios")
        
        try:
            quantidade = int(input("\nQuantas combinações posicionais? (1-20): "))
            
            if quantidade < 1 or quantidade > 20:
                print("❌ Quantidade deve ser entre 1 e 20")
                return
            
            print(f"\n🔄 Gerando {quantidade} combinações com análise posicional...")
            print("⚠️ Este processo pode demorar alguns segundos devido à complexidade...")
            
            combinacoes = self.generator.generate_positional_combinations(quantidade)
            
            if combinacoes:
                self._exibir_combinacoes(combinacoes, "ANÁLISE POSICIONAL AVANÇADA")
                
                # Mostra informações especiais
                print("\n📊 CARACTERÍSTICAS DAS COMBINAÇÕES POSICIONAIS:")
                for i, comb in enumerate(combinacoes, 1):
                    soma = sum(comb)
                    pares = sum(1 for n in comb if n % 2 == 0)
                    print(f"   Comb {i}: Soma={soma}, Pares={pares}, Ímpares={15-pares}")
                
                self._oferecer_salvar(combinacoes)
            else:
                print("❌ Não foi possível gerar combinações posicionais")
                
        except ValueError:
            print("❌ Digite um número válido")
        except Exception as e:
            print(f"❌ Erro: {e}")
    
    def opcao_15_posicional_inteligente(self):
        """Gerador posicional inteligente com análise de ciclos"""
        print("\n🧠 POSICIONAL INTELIGENTE + CICLOS")
        print("-" * 50)
        print("🎯 Análise posicional híbrida com inteligência de ciclos")
        print("📊 Usa padrões da tabela NumerosCiclos para otimizar escolhas")
        print("🔄 Combina o melhor da análise posicional + padrões de urgência")
        
        try:
            # Importa o gerador inteligente
            from gerador_posicional_inteligente import GeradorPosicionalInteligente
            
            # Menu de opções
            print(f"\n🧠 OPÇÕES INTELIGENTES:")
            print(f"   1 - Gerar 1 combinação inteligente (com análise)")
            print(f"   2 - Gerar múltiplas combinações inteligentes")
            print(f"   3 - Analisar padrões de ciclos descobertos")
            print(f"   4 - Comparar: Inteligente vs Posicional tradicional")
            print(f"   0 - Voltar ao menu principal")
            
            opcao = input(f"\nEscolha uma opção: ").strip()
            
            if opcao == "0":
                return
            
            # Cria instância do gerador inteligente
            gerador = GeradorPosicionalInteligente()
            
            if opcao == "1":
                print(f"\n🧠 Gerando combinação posicional inteligente...")
                print(f"⏱️ Analisando padrões de ciclos + posições...")
                
                combinacao = gerador.gerar_combinacao_inteligente(debug=True)
                
                print(f"\n🎯 COMBINAÇÃO INTELIGENTE GERADA:")
                print(f"   🧠 Números: {combinacao}")
                
                soma = sum(combinacao)
                pares = sum(1 for n in combinacao if n % 2 == 0)
                impares = 15 - pares
                
                print(f"\n📊 CARACTERÍSTICAS:")
                print(f"   📊 Soma total: {soma}")
                print(f"   🔢 Pares: {pares}")
                print(f"   🔢 Ímpares: {impares}")
                
                # Oferece salvar
                salvar = input(f"\n💾 Salvar combinação em arquivo? (s/N): ").strip().lower()
                if salvar == 's':
                    self._salvar_combinacao_unica(combinacao, "inteligente")
                
            elif opcao == "2":
                quantidade = int(input("Quantas combinações inteligentes? (1-15): "))
                if quantidade < 1 or quantidade > 15:
                    print("❌ Quantidade deve ser entre 1 e 15")
                    return
                
                print(f"\n🧠 Gerando {quantidade} combinações inteligentes...")
                print(f"⏱️ Analisando ciclos + posições para cada combinação...")
                
                combinacoes = gerador.gerar_multiplas_combinacoes_inteligentes(quantidade)
                
                if combinacoes:
                    print(f"\n🧠 COMBINAÇÕES POSICIONAIS INTELIGENTES:")
                    print("-" * 60)
                    for i, comb in enumerate(combinacoes, 1):
                        print(f" {i:2d}: {' '.join(f'{n:2d}' for n in comb)}")
                    
                    print(f"\n📊 Total: {len(combinacoes)} combinações")
                    
                    print(f"\n📊 CARACTERÍSTICAS DAS COMBINAÇÕES INTELIGENTES:")
                    for i, comb in enumerate(combinacoes, 1):
                        soma = sum(comb)
                        pares = sum(1 for n in comb if n % 2 == 0)
                        print(f"   Comb {i}: Soma={soma}, Pares={pares}, Ímpares={15-pares}")
                    
                    self._oferecer_salvar(combinacoes, "inteligentes")
                else:
                    print("❌ Não foi possível gerar combinações inteligentes")
                
            elif opcao == "3":
                print(f"\n🔍 Analisando padrões de ciclos descobertos...")
                gerador.analisar_padroes_descobertos()
                
            elif opcao == "4":
                print(f"\n🔍 COMPARAÇÃO: Inteligente vs Posicional Tradicional")
                print("-" * 60)
                
                print("🧠 Gerando com sistema INTELIGENTE...")
                comb_inteligente = gerador.gerar_combinacao_inteligente(debug=False)
                
                print("📍 Gerando com sistema TRADICIONAL...")
                from gerador_posicional import GeradorPosicional
                gerador_tradicional = GeradorPosicionalInteligente()
                comb_tradicional = gerador_tradicional.gerador_base.gerar_combinacao_posicional(debug=False)
                
                print(f"\n📊 RESULTADOS DA COMPARAÇÃO:")
                print(f"   🧠 Inteligente: {comb_inteligente}")
                print(f"   📍 Tradicional: {comb_tradicional}")
                
                # Análise das diferenças
                diferenças = set(comb_inteligente) - set(comb_tradicional)
                comuns = set(comb_inteligente) & set(comb_tradicional)
                
                print(f"   🔄 Números únicos (Inteligente): {sorted(diferenças) if diferenças else 'Nenhum'}")
                print(f"   🤝 Números em comum: {len(comuns)}/15")
                
                # Características
                soma_int = sum(comb_inteligente)
                soma_trad = sum(comb_tradicional)
                pares_int = sum(1 for n in comb_inteligente if n % 2 == 0)
                pares_trad = sum(1 for n in comb_tradicional if n % 2 == 0)
                
                print(f"\n📈 CARACTERÍSTICAS COMPARATIVAS:")
                print(f"   📊 Soma - Inteligente: {soma_int} | Tradicional: {soma_trad}")
                print(f"   🔢 Pares - Inteligente: {pares_int} | Tradicional: {pares_trad}")
                
            else:
                print("❌ Opção inválida")
                
        except ImportError as e:
            print(f"❌ Erro ao importar gerador inteligente: {e}")
        except Exception as e:
            print(f"❌ Erro: {e}")
    
    def opcao_16_primos_fibonacci(self):
        """Gerador com inteligência de números primos e Fibonacci"""
        print("\n🔢🌀 GERADOR PRIMOS + FIBONACCI")
        print("-" * 50)
        print("🔢 Análise matemática de números primos")
        print("🌀 Padrões da sequência de Fibonacci")
        print("🧠 Otimização baseada em frequências históricas")
        print("📊 Balanceamento inteligente de quantidades")
        
        try:
            # Inicializa inteligência
            inteligencia = InteligenciaPrimosFibonacci()
            
            if not inteligencia.carregar_dados_historicos():
                print("❌ Erro ao carregar dados históricos")
                return
            
            # Exibe relatório de análise
            print(f"\n📋 ANÁLISE ATUAL:")
            print(f"   🔢 Primos recomendados: {inteligencia.sugerir_quantidade_primos()}")
            print(f"   🌀 Fibonacci recomendados: {inteligencia.sugerir_quantidade_fibonacci()}")
            
            # Menu de opções
            print(f"\n📚 OPÇÕES DISPONÍVEIS:")
            print(f"   1 - Gerar combinação otimizada")
            print(f"   2 - Múltiplas combinações (otimizadas)")
            print(f"   3 - Relatório completo de inteligência")
            print(f"   4 - Avaliar combinação específica")
            
            opcao = input(f"\nEscolha uma opção (1-4): ").strip()
            
            if opcao == "1":
                # Gera combinação única otimizada
                print(f"\n🎯 GERANDO COMBINAÇÃO OTIMIZADA...")
                
                # Gera combinação base aleatória balanceada
                import random
                numeros_base = random.sample(range(1, 26), 15)
                numeros_base.sort()
                
                print(f"   📊 Base inicial: {numeros_base}")
                
                # Otimiza com inteligência primos/Fibonacci
                combinacao_otimizada = inteligencia.otimizar_combinacao(numeros_base, debug=True)
                
                print(f"\n✨ COMBINAÇÃO FINAL:")
                print(f"   🎯 Números: {combinacao_otimizada}")
                
                # Avalia a combinação
                avaliacao = inteligencia.avaliar_combinacao(combinacao_otimizada)
                print(f"   🔢 Primos: {avaliacao['qtd_primos']} (ideal: {avaliacao['primos_ideal']})")
                print(f"   🌀 Fibonacci: {avaliacao['qtd_fibonacci']} (ideal: {avaliacao['fibonacci_ideal']})")
                print(f"   📈 Score geral: {avaliacao['score_geral']:.1f}/100")
                print(f"   ⚖️ Balanceamento: {avaliacao['balanceamento']}")
                
                # Salva combinação
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"combinacao_primos_fibonacci_{timestamp}.txt"
                
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write("🔢🌀 COMBINAÇÃO PRIMOS + FIBONACCI\n")
                    f.write("=" * 50 + "\n")
                    f.write(f"Gerada em: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}\n\n")
                    f.write(f"Números: {','.join(map(str, sorted(combinacao_otimizada)))}\n")
                    f.write(f"Primos ({avaliacao['qtd_primos']}): {avaliacao['primos_presentes']}\n")
                    f.write(f"Fibonacci ({avaliacao['qtd_fibonacci']}): {avaliacao['fibonacci_presentes']}\n")
                    f.write(f"Score: {avaliacao['score_geral']:.1f}/100\n")
                    f.write(f"Balanceamento: {avaliacao['balanceamento']}\n\n")
                    
                    # Adiciona lista simples no final
                    f.write("=" * 50 + "\n")
                    f.write("📋 LISTA SIMPLES DA COMBINAÇÃO:\n")
                    f.write("=" * 50 + "\n")
                    f.write(f"{','.join(map(str, sorted(combinacao_otimizada)))}\n")
                
                print(f"💾 Combinação salva em: {filename}")
                
            elif opcao == "2":
                # Múltiplas combinações
                try:
                    quantidade = int(input("Quantas combinações gerar? "))
                    quantidade = max(1, min(50, quantidade))  # Limita entre 1 e 50
                    
                    print(f"\n🎯 GERANDO {quantidade} COMBINAÇÕES OTIMIZADAS...")
                    
                    combinacoes = []
                    import random
                    
                    for i in range(quantidade):
                        print(f"\n--- Combinação {i+1}/{quantidade} ---")
                        
                        # Gera base aleatória
                        numeros_base = random.sample(range(1, 26), 15)
                        numeros_base.sort()
                        
                        # Otimiza
                        combinacao_otimizada = inteligencia.otimizar_combinacao(numeros_base, debug=False)
                        avaliacao = inteligencia.avaliar_combinacao(combinacao_otimizada)
                        
                        combinacoes.append({
                            'numeros': combinacao_otimizada,
                            'avaliacao': avaliacao
                        })
                        
                        print(f"   {combinacao_otimizada} | Score: {avaliacao['score_geral']:.1f}")
                    
                    # Ordena por score
                    combinacoes.sort(key=lambda x: x['avaliacao']['score_geral'], reverse=True)
                    
                    print(f"\n🏆 TOP 3 MELHORES COMBINAÇÕES:")
                    for i, comb in enumerate(combinacoes[:3]):
                        print(f"   {i+1}º: {comb['numeros']} (Score: {comb['avaliacao']['score_geral']:.1f})")
                    
                    # Salva todas
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    filename = f"combinacoes_primos_fibonacci_{quantidade}x_{timestamp}.txt"
                    
                    with open(filename, 'w', encoding='utf-8') as f:
                        f.write(f"🔢🌀 {quantidade} COMBINAÇÕES PRIMOS + FIBONACCI\n")
                        f.write("=" * 60 + "\n")
                        f.write(f"Geradas em: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}\n\n")
                        
                        for i, comb in enumerate(combinacoes):
                            f.write(f"Combinação {i+1:2d}: {','.join(map(str, sorted(comb['numeros'])))}\n")
                            f.write(f"   Score: {comb['avaliacao']['score_geral']:.1f}/100\n")
                            f.write(f"   Primos: {comb['avaliacao']['qtd_primos']} | Fibonacci: {comb['avaliacao']['qtd_fibonacci']}\n")
                            f.write(f"   Balanceamento: {comb['avaliacao']['balanceamento']}\n\n")
                        
                        # Adiciona lista simples no final
                        f.write("=" * 60 + "\n")
                        f.write("📋 LISTA SIMPLES DAS COMBINAÇÕES:\n")
                        f.write("=" * 60 + "\n")
                        for i, comb in enumerate(combinacoes):
                            f.write(f"{','.join(map(str, sorted(comb['numeros'])))}\n")
                    
                    print(f"💾 {quantidade} combinações salvas em: {filename}")
                    
                except ValueError:
                    print("❌ Quantidade inválida")
                    
            elif opcao == "3":
                # Relatório completo
                print("\n📋 RELATÓRIO COMPLETO DE INTELIGÊNCIA:")
                print(inteligencia.relatorio_inteligencia())
                
            elif opcao == "4":
                # Avalia combinação específica
                print(f"\n🔍 AVALIAÇÃO DE COMBINAÇÃO ESPECÍFICA")
                print(f"Digite 15 números separados por vírgula ou espaço:")
                
                entrada = input("Números: ").strip()
                try:
                    # Tenta diferentes separadores
                    if ',' in entrada:
                        numeros = [int(x.strip()) for x in entrada.split(',')]
                    else:
                        numeros = [int(x.strip()) for x in entrada.split()]
                    
                    if len(numeros) != 15:
                        print(f"❌ Insira exatamente 15 números. Você inseriu {len(numeros)}")
                        return
                    
                    if not all(1 <= n <= 25 for n in numeros):
                        print("❌ Todos os números devem estar entre 1 e 25")
                        return
                    
                    if len(set(numeros)) != 15:
                        print("❌ Não pode haver números repetidos")
                        return
                    
                    numeros.sort()
                    avaliacao = inteligencia.avaliar_combinacao(numeros)
                    
                    print(f"\n📊 AVALIAÇÃO DA COMBINAÇÃO: {numeros}")
                    print(f"   🔢 Primos: {avaliacao['qtd_primos']} (ideal: {avaliacao['primos_ideal']})")
                    print(f"   🌀 Fibonacci: {avaliacao['qtd_fibonacci']} (ideal: {avaliacao['fibonacci_ideal']})")
                    print(f"   🎯 Números especiais (primo+fibonacci): {avaliacao['qtd_especiais']}")
                    print(f"   📈 Score primos: {avaliacao['score_primos']:.1f}/100")
                    print(f"   📈 Score fibonacci: {avaliacao['score_fibonacci']:.1f}/100")
                    print(f"   📈 Score geral: {avaliacao['score_geral']:.1f}/100")
                    print(f"   ⚖️ Balanceamento: {avaliacao['balanceamento']}")
                    
                    if avaliacao['primos_presentes']:
                        print(f"   🔢 Primos encontrados: {avaliacao['primos_presentes']}")
                    if avaliacao['fibonacci_presentes']:
                        print(f"   🌀 Fibonacci encontrados: {avaliacao['fibonacci_presentes']}")
                    if avaliacao['especiais_presentes']:
                        print(f"   ✨ Especiais encontrados: {avaliacao['especiais_presentes']}")
                    
                except ValueError:
                    print("❌ Formato inválido. Use números separados por vírgula ou espaço")
                    
            else:
                print("❌ Opção inválida")
                
        except ImportError as e:
            print(f"❌ Erro ao importar inteligência primos/fibonacci: {e}")
        except Exception as e:
            print(f"❌ Erro: {e}")
    
    def opcao_17_gerador_hibrido_completo(self):
        """Gerador híbrido que integra TODOS os métodos disponíveis"""
        print("\n🌟 GERADOR HÍBRIDO COMPLETO")
        print("-" * 60)
        print("🔥 Integração de TODOS os métodos de análise:")
        print("   📍 Análise posicional avançada")
        print("   🔄 Ciclos e tendências temporais")
        print("   🔢 Números primos otimizados")
        print("   🌀 Sequência de Fibonacci")
        print("   ➕ Controle de soma ideal")
        print("   🔀 Balanceamento ímpar/par")
        print("   📐 Distribuição por quintis")
        print("   🎯 Padrões avançados (gaps, sequências)")
        
        try:
            # Inicializa gerador híbrido
            gerador_hibrido = GeradorHibridoCompleto()
            
            if not gerador_hibrido.carregar_dados_completos():
                print("❌ Erro ao carregar dados para análise híbrida")
                return
            
            # Menu de opções
            print(f"\n📚 OPÇÕES DO GERADOR HÍBRIDO:")
            print(f"   1 - Gerar combinação híbrida única")
            print(f"   2 - Múltiplas combinações híbridas")
            print(f"   3 - Análise detalhada de combinação")
            print(f"   4 - Relatório de padrões completos")
            
            opcao = input(f"\nEscolha uma opção (1-4): ").strip()
            
            if opcao == "1":
                # Combinação única com análise completa
                print(f"\n🌟 GERANDO COMBINAÇÃO HÍBRIDA ÚNICA...")
                
                combinacao = gerador_hibrido.gerar_combinacao_hibrida(debug=True)
                
                print(f"\n📋 RELATÓRIO COMPLETO:")
                relatorio = gerador_hibrido.relatorio_combinacao_hibrida(combinacao)
                print(relatorio)
                
                # Salva combinação
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"combinacao_hibrida_{timestamp}.txt"
                
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write("🌟 COMBINAÇÃO HÍBRIDA COMPLETA\n")
                    f.write("=" * 60 + "\n")
                    f.write(f"Gerada em: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}\n\n")
                    f.write(relatorio)
                    
                    # Adiciona lista simples no final
                    f.write("\n" + "=" * 60 + "\n")
                    f.write("📋 LISTA SIMPLES DA COMBINAÇÃO:\n")
                    f.write("=" * 60 + "\n")
                    f.write(f"{','.join(map(str, sorted(combinacao)))}\n")
                
                print(f"\n💾 Combinação salva em: {filename}")
                
            elif opcao == "2":
                # Múltiplas combinações
                try:
                    quantidade = int(input("Quantas combinações gerar? "))
                    quantidade = max(1, min(20, quantidade))  # Limita entre 1 e 20
                    
                    print(f"\n🚀 GERANDO {quantidade} COMBINAÇÕES HÍBRIDAS...")
                    
                    combinacoes = gerador_hibrido.gerar_multiplas_combinacoes_hibridas(quantidade, debug=True)
                    
                    print(f"\n🏆 MELHORES COMBINAÇÕES:")
                    for i, combo in enumerate(combinacoes[:5]):  # Top 5
                        print(f"   {i+1}º: {combo['combinacao']} (Score: {combo['score_final']:.1f})")
                    
                    # Salva todas
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    filename = f"combinacoes_hibridas_{quantidade}x_{timestamp}.txt"
                    
                    with open(filename, 'w', encoding='utf-8') as f:
                        f.write(f"🌟 {quantidade} COMBINAÇÕES HÍBRIDAS COMPLETAS\n")
                        f.write("=" * 70 + "\n")
                        f.write(f"Geradas em: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}\n\n")
                        
                        for i, combo in enumerate(combinacoes):
                            f.write(f"Combinação {i+1:2d}: {','.join(map(str, sorted(combo['combinacao'])))}\n")
                            f.write(f"   Score Final: {combo['score_final']:.1f}/100\n")
                            f.write(f"   Soma: {combo['analise']['soma']}\n")
                            f.write(f"   Ímpares: {combo['analise']['impares']} | Pares: {combo['analise']['pares']}\n")
                            f.write(f"   Primos: {combo['analise']['primos']} | Fibonacci: {combo['analise']['fibonacci']}\n")
                            f.write(f"   Quintis: {combo['analise']['quintis']}\n\n")
                        
                        # Adiciona lista simples no final
                        f.write("=" * 70 + "\n")
                        f.write("📋 LISTA SIMPLES DAS COMBINAÇÕES:\n")
                        f.write("=" * 70 + "\n")
                        for i, combo in enumerate(combinacoes):
                            f.write(f"{','.join(map(str, sorted(combo['combinacao'])))}\n")
                    
                    print(f"💾 {quantidade} combinações salvas em: {filename}")
                    
                except ValueError:
                    print("❌ Quantidade inválida")
                    
            elif opcao == "3":
                # Análise de combinação específica
                print(f"\n🔍 ANÁLISE DETALHADA DE COMBINAÇÃO")
                print(f"Digite 15 números separados por vírgula ou espaço:")
                
                entrada = input("Números: ").strip()
                try:
                    # Processa entrada
                    if ',' in entrada:
                        numeros = [int(x.strip()) for x in entrada.split(',')]
                    else:
                        numeros = [int(x.strip()) for x in entrada.split()]
                    
                    if len(numeros) != 15:
                        print(f"❌ Insira exatamente 15 números. Você inseriu {len(numeros)}")
                        return
                    
                    if not all(1 <= n <= 25 for n in numeros):
                        print("❌ Todos os números devem estar entre 1 e 25")
                        return
                    
                    if len(set(numeros)) != 15:
                        print("❌ Não pode haver números repetidos")
                        return
                    
                    numeros.sort()
                    print(f"\n📊 ANÁLISE HÍBRIDA COMPLETA: {numeros}")
                    
                    relatorio = gerador_hibrido.relatorio_combinacao_hibrida(numeros)
                    print(relatorio)
                    
                except ValueError:
                    print("❌ Formato inválido. Use números separados por vírgula ou espaço")
                    
            elif opcao == "4":
                # Relatório de padrões
                print(f"\n📊 RELATÓRIO DE PADRÕES HISTÓRICOS:")
                print(f"   ➕ Soma média: {gerador_hibrido.padroes_soma['media']:.1f} ± {gerador_hibrido.padroes_soma['desvio_padrao']:.1f}")
                print(f"   🔀 Ímpares médio: {gerador_hibrido.padroes_impares['media']:.1f}")
                print(f"   📐 Quintis ideais: {gerador_hibrido.padroes_quintis['balanceamento_ideal']}")
                print(f"   🕳️ Gaps médio: {gerador_hibrido.padroes_gaps['media']:.1f}")
                print(f"   📏 Distância extremos: {gerador_hibrido.padroes_extremos['distancia_media']:.1f}")
                print(f"   🔢 Múltiplos de 3: {gerador_hibrido.padroes_multiplos['multiplos3_media']:.1f}")
                
                print(f"\n⚖️ PESOS ATUAIS DO ALGORITMO:")
                for chave, peso in gerador_hibrido.pesos.items():
                    print(f"   {chave}: {peso:.3f} ({peso*100:.1f}%)")
                    
            else:
                print("❌ Opção inválida")
                
        except ImportError as e:
            print(f"❌ Erro ao importar gerador híbrido: {e}")
        except Exception as e:
            print(f"❌ Erro: {e}")
    
    def opcao_18_backtesting_posicional(self):
        """Executa backtesting do sistema posicional"""
        print("\n📊 BACKTESTING ANÁLISE POSICIONAL")
        print("-" * 50)
        print("🔬 Análise de performance das combinações geradas")
        print("📈 Validação dos algoritmos acadêmicos implementados")
        print("🎯 Teste histórico de acertos e proximidade")
        
        try:
            # Importa o sistema de backtesting
            from backtesting_posicional import BacktestingPosicional
            
            # Menu de opções de backtesting
            print(f"\n🎯 OPÇÕES DE BACKTESTING:")
            print(f"   1 - Backtesting último ano (rápido ~5 min)")
            print(f"   2 - Backtesting últimos 2 anos (médio ~15 min)")
            print(f"   3 - Backtesting últimos 3 anos (completo ~30 min)")
            print(f"   4 - Backtesting período customizado")
            print(f"   0 - Voltar ao menu principal")
            
            opcao = input(f"\nEscolha uma opção: ").strip()
            
            if opcao == "0":
                return
            
            # Cria instância do backtesting
            backtesting = BacktestingPosicional()
            
            if opcao == "1":
                print(f"\n🚀 Iniciando backtesting do último ano...")
                print(f"⏱️ Este processo pode demorar alguns minutos...")
                backtesting.executar_backtesting_completo(anos_teste=1, combinacoes_por_concurso=3)
                
            elif opcao == "2":
                print(f"\n🚀 Iniciando backtesting dos últimos 2 anos...")
                print(f"⏱️ Este processo pode demorar até 15 minutos...")
                backtesting.executar_backtesting_completo(anos_teste=2, combinacoes_por_concurso=5)
                
            elif opcao == "3":
                print(f"\n🚀 Iniciando backtesting dos últimos 3 anos...")
                print(f"⏱️ Este processo pode demorar até 30 minutos...")
                backtesting.executar_backtesting_completo(anos_teste=3, combinacoes_por_concurso=5)
                
            elif opcao == "4":
                # Período customizado
                print(f"\n📅 PERÍODO CUSTOMIZADO:")
                concurso_inicial = int(input("Concurso inicial: "))
                concurso_final = int(input("Concurso final: "))
                combinacoes = int(input("Combinações por concurso (1-20): "))
                
                print(f"\n🚀 Iniciando backtesting personalizado...")
                print(f"📊 Período: {concurso_inicial} até {concurso_final}")
                print(f"🎲 {combinacoes} combinações por concurso")
                
                resultados = backtesting.simular_periodo_historico(
                    concurso_inicial, concurso_final, combinacoes
                )
                analise = backtesting.analisar_resultados(resultados)
                backtesting.exibir_relatorio(analise, f"({concurso_inicial}-{concurso_final})")
                
            else:
                print("❌ Opção inválida")
                
        except ImportError as e:
            print(f"❌ Erro ao importar módulo de backtesting: {e}")
        except Exception as e:
            print(f"❌ Erro durante backtesting: {e}")
    
    def opcao_19_testes_temporais(self):
        """Executa testes temporais e validação"""
        print("\n🕰️ TESTES TEMPORAIS & VALIDAÇÃO")
        print("-" * 50)
        print("🎯 Teste de predições em concursos passados")
        print("📊 Backtesting científico dos algoritmos")
        print("⚔️ Comparação entre geradores")
        print("🔬 Validação temporal da inteligência artificial")
        
        try:
            # Cria instância da interface de testes temporais
            interface_testes = TesteTemporalInteligente()
            
            # Executa o menu principal dos testes temporais
            interface_testes.menu_principal()
            
        except ImportError as e:
            print(f"❌ Erro ao importar módulo de testes temporais: {e}")
        except Exception as e:
            print(f"❌ Erro durante testes temporais: {e}")
    
    def opcao_20_status_sistema(self):
        """Exibe status do sistema"""
        print("\n📊 STATUS DO SISTEMA")
        print("-" * 40)
        
        # Status da conexão
        print("🔗 Conexão com banco:")
        if db_config.test_connection():
            print("   ✅ Conectado")
            
            # Estatísticas da base
            resultado = db_config.execute_query("SELECT COUNT_BIG(*) FROM Resultados_INT")
            if resultado:
                total_concursos = resultado[0][0]
                print(f"   📊 Total de concursos: {total_concursos}")
            
            resultado = db_config.execute_query("SELECT MAX(Concurso) FROM Resultados_INT")
            if resultado and resultado[0][0]:
                ultimo_base = resultado[0][0]
                print(f"   🎯 Último concurso: {ultimo_base}")
        else:
            print("   ❌ Desconectado")
        
        # Status da API
        print("\n🌐 API da Caixa:")
        ultimo_api = self.menu_lotofacil.obter_ultimo_concurso_api()
        if ultimo_api > 0:
            print(f"   ✅ Acessível (último: {ultimo_api})")
        else:
            print("   ❌ Inacessível")
        
        # Status do gerador
        print("\n🎲 Gerador:")
        print(f"   📋 Obrigatórios: {len(self.generator.numeros_obrigatorios)}")
        print(f"   🚫 Proibidos: {len(self.generator.numeros_proibidos)}")
        
        # Memória/Cache
        print("\n💾 Cache:")
        if self.generator._cache_frequencias:
            print("   ✅ Frequências carregadas")
        else:
            print("   ⚪ Frequências não carregadas")
        
        if self.generator._cache_ciclos:
            print("   ✅ Ciclos carregados")
        else:
            print("   ⚪ Ciclos não carregados")
    
    def opcao_21_limpar_cache(self):
        """Limpa cache do sistema"""
        print("\n🧹 LIMPAR CACHE DO SISTEMA")
        print("-" * 40)
        
        self.generator._cache_frequencias = None
        self.generator._cache_ciclos = None
        
        print("✅ Cache limpo!")
        print("💡 Dados serão recarregados na próxima geração")
    
    def _exibir_combinacoes(self, combinacoes: list, titulo: str):
        """Exibe combinações formatadas"""
        if not combinacoes:
            print("❌ Nenhuma combinação gerada")
            return
        
        print(f"\n🎯 COMBINAÇÕES {titulo}")
        print("-" * 50)
        
        for i, comb in enumerate(combinacoes, 1):
            numeros_fmt = " ".join(f"{n:2d}" for n in comb)
            print(f"{i:2d}: {numeros_fmt}")
        
        print(f"\n📊 Total: {len(combinacoes)} combinações")
    
    def _oferecer_salvar(self, combinacoes: list, tipo: str = ""):
        """Oferece opção de salvar combinações"""
        if not combinacoes:
            return
        
        tipo_nome = f"_{tipo}" if tipo else ""
        salvar = input("\n💾 Salvar combinações em arquivo? (s/N): ").strip().lower()
        if salvar == 's':
            nome = input("Nome do arquivo (Enter para automático): ").strip()
            if not nome:
                nome = None
            
            # Salva usando o gerador base
            if hasattr(self, 'generator'):
                self.generator.salvar_combinacoes(combinacoes, nome)
            else:
                # Fallback para salvar diretamente
                import datetime
                import os
                
                if not nome:
                    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                    nome = f"combinacoes{tipo_nome}_{timestamp}.txt"
                
                if not nome.endswith('.txt'):
                    nome += '.txt'
                
                pasta_resultados = os.path.join(os.path.dirname(__file__), "resultados")
                os.makedirs(pasta_resultados, exist_ok=True)
                
                caminho_arquivo = os.path.join(pasta_resultados, nome)
                
                with open(caminho_arquivo, 'w', encoding='utf-8') as f:
                    f.write(f"# Combinações {tipo}\n")
                    f.write(f"# Gerado em: {datetime.datetime.now().strftime('%d/%m/%Y às %H:%M:%S')}\n")
                    f.write(f"# Total: {len(combinacoes)} combinações\n\n")
                    
                    for i, comb in enumerate(combinacoes, 1):
                        numeros = ' '.join(f'{n:02d}' for n in comb)
                        f.write(f"{i:03d}: {numeros}\n")
                
                print(f"✅ Salvo em: {caminho_arquivo}")
    
    def _salvar_combinacao_unica(self, combinacao: list, tipo: str = ""):
        """Salva uma única combinação"""
        self._oferecer_salvar([combinacao], tipo)
    
    def executar(self):
        """Execução principal do menu"""
        print("🎯 INICIANDO LOTOFÁCIL LITE...")
        
        # Teste inicial de conexão
        if not db_config.test_connection():
            print("⚠️ ATENÇÃO: Problema na conexão com banco de dados")
            print("   Algumas funcionalidades podem não funcionar")
            print("   Use a opção 1 para mais detalhes")
        
        while True:
            try:
                self.exibir_menu_principal()
                opcao = input("\nEscolha uma opção: ").strip()
                
                if opcao == "0":
                    print("\n👋 Saindo do sistema...")
                    break
                elif opcao == "1":
                    self.opcao_1_testar_conexao()
                elif opcao == "2":
                    self.opcao_2_ultimo_concurso_api()
                elif opcao == "3":
                    self.opcao_3_atualizar_especifico()
                elif opcao == "4":
                    self.opcao_4_atualizacao_completa()
                elif opcao == "5":
                    self.opcao_5_atualizar_range()
                elif opcao == "6":
                    self.opcao_6_combinacoes_aleatorias()
                elif opcao == "7":
                    self.opcao_7_combinacoes_frequencia()
                elif opcao == "8":
                    self.opcao_8_combinacoes_ciclos()
                elif opcao == "9":
                    self.opcao_9_combinacoes_balanceadas()
                elif opcao == "10":
                    self.opcao_10_combinacoes_padroes()
                elif opcao == "11":
                    self.opcao_11_expandir_quina()
                elif opcao == "12":
                    self.opcao_12_configurar_intuicao()
                elif opcao == "13":
                    self.opcao_13_mix_personalizado()
                elif opcao == "14":
                    self.opcao_14_analise_posicional()
                elif opcao == "15":
                    self.opcao_15_posicional_inteligente()
                elif opcao == "16":
                    self.opcao_16_primos_fibonacci()
                elif opcao == "17":
                    self.opcao_17_gerador_hibrido_completo()
                elif opcao == "18":
                    self.opcao_18_backtesting_posicional()
                elif opcao == "19":
                    self.opcao_19_testes_temporais()
                elif opcao == "20":
                    self.opcao_20_status_sistema()
                elif opcao == "21":
                    self.opcao_21_limpar_cache()
                else:
                    print("❌ Opção inválida")
                
                input("\nPressione Enter para continuar...")
                
            except KeyboardInterrupt:
                print("\n\n👋 Interrompido pelo usuário. Saindo...")
                break
            except Exception as e:
                print(f"\n❌ Erro inesperado: {e}")
                input("Pressione Enter para continuar...")

if __name__ == "__main__":
    menu = MainMenu()
    menu.executar()
